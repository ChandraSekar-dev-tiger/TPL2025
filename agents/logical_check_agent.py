from typing import TypedDict, Optional, List
from agents.llm_client import llm_client
from prompts.prompt_templates import logical_check_prompt_template
import logging
import traceback
import json

logger = logging.getLogger("agents.logical_check_agent")

class LogicalCheckState(TypedDict):
    query: str
    code: Optional[str]
    language: Optional[str]
    logical_errors: Optional[List[str]]
    error_message: Optional[str]
    error_trace: Optional[str]
    current_node: Optional[str]
    codegen_attempts: Optional[int]

def logical_check_agent(state: LogicalCheckState) -> LogicalCheckState:
    logger.info("Starting logical check agent")
    logger.debug("Current state: %s", json.dumps(state, default=str))
    
    try:
        state["current_node"] = "logical_check"
        if not state.get("code"):
            logger.warning("No code to check")
            error_msg = "No code provided for logical check"
            state["logical_errors"] = [error_msg]
            return state

        current_attempt = state.get("codegen_attempts", 0)
        logger.info(f"Logical check attempt {current_attempt}/3")

        # Prepare the prompt
        prompt_text = logical_check_prompt_template.format(
            query=state["query"],
            code=state["code"],
            language=state.get("language", "python")
        )

        response = llm_client.call_llm(prompt_text)
        logical_errors = json.loads(response)
        state["logical_errors"] = logical_errors
        # state["logical_errors"] = []

        return state

    except Exception as e:
        logger.error("Logical check failed: %s", str(e), exc_info=True)
        error_msg = f"Logical check failed: {str(e)}"
        state["logical_errors"] = []
        state["error_message"] = error_msg
        state["error_trace"] = traceback.format_exc()
    
    logger.info("Logical check agent completed. State updated with %s", 
                "errors" if state.get("logical_errors") else "success")
    return state