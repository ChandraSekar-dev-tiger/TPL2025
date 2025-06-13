from typing import TypedDict, Optional
import subprocess
import logging

logger = logging.getLogger(__name__)

class ExecutionState(TypedDict):
    query: str
    intent: str
    confidence: float
    code: str
    language: str
    result: Optional[str]
    success: Optional[bool]
    error_message: Optional[str]

def execution_agent(state: ExecutionState) -> ExecutionState:
    try:
        if state["language"].lower() == "python":
            # You can improve this sandboxing/execution method as needed
            exec_globals = {}
            exec(state["code"], exec_globals)
            result = exec_globals.get("result", "No result variable set")
            state["result"] = result
            state["success"] = True
            logger.info("Python code executed successfully")
        else:
            # Add other language execution logic if needed
            state["result"] = None
            state["success"] = False
            state["error_message"] = f"Unsupported language: {state['language']}"
            logger.error(state["error_message"])
    except Exception as e:
        state["result"] = None
        state["success"] = False
        state["error_message"] = str(e)
        logger.error(f"Execution error: {e}")
    return state
