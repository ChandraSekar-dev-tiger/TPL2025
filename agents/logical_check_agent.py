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

def logical_check_agent(state: LogicalCheckState) -> LogicalCheckState:
    logger.info("Starting logical check agent")
    logger.debug("Current state: %s", json.dumps(state, default=str))
    
    try:
        # Set current node
        state["current_node"] = "logical_check"
        
        # Check if code exists
        if not state.get("code"):
            logger.warning("No code to check")
            state["logical_errors"] = ["No code provided for logical check"]
            return state
            
        # Generate prompt for logical check
        prompt_text = logical_check_prompt_template.format_prompt(
            query=state.get("query", ""),
            code=state["code"],
            language=state.get("language", "python")
        )
        logger.debug("Generated prompt: %s", prompt_text)
        
        try:
            # TODO: Replace with actual LLM call
            # response = llm_client.call_llm(prompt_text)
            # logical_errors = json.loads(response)
            
            # Dummy response for testing
            logical_errors = []
            
            state["logical_errors"] = logical_errors
            if logical_errors:
                logger.warning("Logical errors found: %s", json.dumps(logical_errors))
            else:
                logger.info("No logical errors found")
                
        except Exception as e:
            logger.error("LLM call failed: %s", str(e), exc_info=True)
            state["logical_errors"] = [f"Failed to perform logical check: {str(e)}"]
            state["error_message"] = f"LLM call failed: {str(e)}"
            state["error_trace"] = traceback.format_exc()
            
    except Exception as e:
        logger.error("Logical check failed: %s", str(e), exc_info=True)
        state["logical_errors"] = [f"Logical check failed: {str(e)}"]
        state["error_message"] = f"Logical check failed: {str(e)}"
        state["error_trace"] = traceback.format_exc()
    
    logger.info("Logical check agent completed. State updated with %s", 
                "errors" if state.get("logical_errors") else "success")
    return state 