from typing import TypedDict, Optional
from agents.llm_client import llm_client
from prompts.prompt_templates import codegen_prompt_template
import json
import logging
import traceback

logger = logging.getLogger(__name__)

class CodegenState(TypedDict):
    query: str
    intent: Optional[str]
    confidence: Optional[float]
    filtered_metadata: Optional[dict]
    code: Optional[str]
    language: Optional[str]
    error_message: Optional[str]
    error_trace: Optional[str]

def code_generation_agent(state: CodegenState) -> CodegenState:
    try:
        prompt_text = codegen_prompt_template.format_prompt(
            intent=state["intent"], 
            filtered_metadata=state["filtered_metadata"],
            language=state.get("language", "python"),
            query=state["query"], 
        )
        try:
            #TODO: change dummy llm return
            j = {"code":"""total_sales_by_category = df.groupby("category")["sales"].sum().reset_index()""", "language": "python"}

            # response = llm_client.call_llm(prompt_text)
            # j = json.loads(response)
            state["code"] = j.get("code", "")
            state["language"] = j.get("language", "python")
            logger.info(f"Generated code in {state['language']}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {str(e)}")
            state["code"] = ""
            state["language"] = None
            state["error_message"] = f"Failed to parse LLM response: {str(e)}"
            state["error_trace"] = traceback.format_exc()
        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            state["code"] = ""
            state["language"] = None
            state["error_message"] = f"LLM call failed: {str(e)}"
            state["error_trace"] = traceback.format_exc()
    except Exception as e:
        logger.error(f"Code generation failed: {str(e)}")
        state["code"] = ""
        state["language"] = None
        state["error_message"] = f"Code generation failed: {str(e)}"
        state["error_trace"] = traceback.format_exc()
    return state
