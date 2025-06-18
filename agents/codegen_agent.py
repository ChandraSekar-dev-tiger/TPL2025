from typing import TypedDict, Optional
from agents.llm_client import llm_client
from prompts.prompt_templates import codegen_prompt_template
import logging
import traceback
import json

logger = logging.getLogger("agents.codegen_agent")

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

async def code_generation_agent(state: CodegenState) -> CodegenState:
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

        filtered_metadata = json.dumps(state.get("filtered_metadata", []), indent=2)
        
        # Example dummy code for LLM:
        prompt = codegen_prompt_template.format(
            query=state["query"],
            intent=state.get("intent", "unknown"),
            filtered_metadata=filtered_metadata,
            logical_errors=json.dumps(logical_errors, indent=2),
            syntax_errors=json.dumps(syntax_errors, indent=2),
            language=state.get("language", "sql"),
        )
        response = llm_client.call_llm(prompt)
        logger.info("code gen response: %s", response)
        state["code"] = response
        state["language"] = "sql"
            
        # For now, just return dummy code
        logger.info("Generating code")
        state["code"] = "SELECT * FROM `dbx-azure-catalog`.code_claws.department_table LIMIT 10"
        state["language"] = "sql"
        state["error_message"] = None
        return state
        
    except Exception as e:
        logger.error(f"Error in code generation: {str(e)}")
        error_msg = f"Error in code generation: {str(e)}"
        state["error_message"] = error_msg
        state["error_trace"] = traceback.format_exc()
        state["code"] = None
        return state