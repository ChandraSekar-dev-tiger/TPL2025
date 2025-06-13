import logging
from typing import TypedDict, Optional, Any
from core.execute_code_tool import execute_code

logger = logging.getLogger(__name__)

class ExecutionState(TypedDict):
    query: str
    intent: str
    confidence: float
    code: str
    language: str
    result: Optional[Any]
    success: Optional[bool]
    error_message: Optional[str]

def execution_agent(state: ExecutionState) -> ExecutionState:
    try:
        result = execute_code(state["code"], state["language"])
        state["result"] = result
        state["success"] = True
        state["error_message"] = None
        logger.info("Code execution successful.")
        return state
    except Exception as e:
        logger.error(f"Execution error: {e}")
        state["result"] = None
        state["success"] = False
        state["error_message"] = str(e)
        return state
