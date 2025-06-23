import difflib
import json
import logging
import re
import traceback
from typing import Optional, TypedDict

import pandas as pd

from agents.llm_client import llm_client
from guardrail_copy import apply_guardrails
from prompts.prompt_templates import codegen_prompt_template

logger = logging.getLogger("agents.codegen_agent")

with open(
    "/mnt/d/TigerAnalytics/Hackathon/AI Enthusiast/TPL2025/metadata/NonClinical_sheets_data.json",
    "r",
) as f:
    all_data_description = json.load(f)


class CodegenState(TypedDict):
    query: str
    intent: Optional[str]
    confidence: Optional[float]
    filtered_metadata: Optional[dict]
    code: Optional[str]
    language: Optional[str]
    error_message: Optional[str]
    error_trace: Optional[str]
    current_node: Optional[str]
    codegen_attempts: Optional[int]
    max_codegen_attempts: Optional[int]
    logical_errors: Optional[list]
    syntax_errors: Optional[list]


def code_generation_agent(state: CodegenState, role: str) -> CodegenState:
    """Generate code based on the query and metadata."""
    try:
        # Get current attempt number
        current_attempt = state.get("codegen_attempts", 0)
        logger.info(f"Starting code generation agent (attempt {current_attempt + 1}/3)")

        # Increment attempt counter
        state["codegen_attempts"] = current_attempt + 1

        # Log errors for debugging
        logical_errors = state.get("logical_errors", [])
        syntax_errors = state.get("syntax_errors", [])
        logger.info("Logical errors: %s", logical_errors)
        logger.info("Syntax errors: %s", syntax_errors)

        filtered_metadata_jsn = state.get("filtered_metadata", [])
        filtered_metadata = json.dumps(filtered_metadata_jsn, indent=2)

        # extract the table names from filtered data
        table_names = list(
            set([filtered_rec["table_name"] for filtered_rec in filtered_metadata_jsn])
        )
        # in the combined json filter for the extracted tables
        table_name_description = {}
        for table_name in table_names:
            matches = difflib.get_close_matches(
                table_name, all_data_description.keys(), n=1, cutoff=0.6
            )
            logger.info("Matching table name: %s", matches[0])
            table_name_description["`dbx-azure-catalog`.code_claws." + matches[0]] = (
                all_data_description[matches[0]]
            )

        # pass it as a table description in the prompt > pass to line 56
        filtered_table_description = table_name_description

        # Example dummy code for LLM:
        prompt = codegen_prompt_template.format(
            query=state["query"],
            intent=state.get("intent", "unknown"),
            filtered_metadata=filtered_metadata,
            table_description=filtered_table_description,
            logical_errors=json.dumps(logical_errors, indent=2),
            syntax_errors=json.dumps(syntax_errors, indent=2),
            language=state.get("language", "sql"),
        )
        logger.info("Generating code")
        response = llm_client.call_llm(prompt)
        logger.info("code gen response: %s", response)

        match = re.search(r"```sql(.*?)```", response, re.DOTALL)
        if match:
            query = match.group(1).strip()
            logger.info("code gen clean response: %s", query)
            state["code"] = query
            state["language"] = "sql"
            state["error_message"] = None

            logger.info("Applying guardrails")
            violations = apply_guardrails(
                query=state["query"],
                role=role,
                table=table_names,
                code=query,
            )
            if violations:
                logger.warning(
                    f"Query blocked due to guardrail violations: {violations}"
                )
                return {
                    "session_id": None,
                    "result": {
                        "report": {
                            "report_text": "Your query was blocked due to policy violations.",
                            "violations": violations,
                        },
                        "session_state": None,
                    },
                }

        else:
            print("No SQL query found.")
            state["code"] = None
            state["language"] = "sql"
            state["error_message"] = "Format issue"

        # For now, just return dummy code
        # logger.info("Generating code")
        # state["code"] = "SELECT * FROM `dbx-azure-catalog`.code_claws.department_table LIMIT 10"
        # state["language"] = "sql"

        return state

    except Exception as e:
        logger.error(f"Error in code generation: {str(e)}")
        error_msg = f"Error in code generation: {str(e)}"
        state["error_message"] = error_msg
        state["error_trace"] = traceback.format_exc()
        state["code"] = None
        return state
