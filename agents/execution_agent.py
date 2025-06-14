from typing import TypedDict, Optional, Any
import subprocess
import logging
import traceback

logger = logging.getLogger(__name__)

class ExecutionState(TypedDict):
    query: str
    intent: Optional[str]
    confidence: Optional[float]
    code: Optional[str]
    language: Optional[str]
    result: Optional[Any]
    success: Optional[bool]
    error_message: Optional[str]
    error_trace: Optional[str]

def execution_agent(state: ExecutionState) -> ExecutionState:
    try:
        if not state.get("code"):
            state["success"] = False
            state["error_message"] = "No code provided for execution"
            state["error_trace"] = traceback.format_exc()
            return state

        if state.get("language", "").lower() == "python":
            try:
                #TODO:
                import pandas as pd
                data = {
                    "date": ["2025-06-01", "2025-06-02", "2025-06-03", "2025-06-04"],
                    "category": ["Electronics", "Clothing", "Electronics", "Books"],
                    "sales": [1500, 700, 1200, 300],
                    "units_sold": [3, 5, 2, 7],
                    "region": ["North", "South", "East", "West"]
                }
                df = pd.DataFrame(data)

                # # You can improve this sandboxing/execution method as needed
                # exec_globals = {}
                # exec(state["code"], exec_globals)
                # result = exec_globals.get("result", "No result variable set")

                result = df

                state["result"] = result
                state["success"] = True
                state["error_message"] = None
                state["error_trace"] = None
                logger.info("Python code executed successfully")
            except ImportError as e:
                logger.error(f"Required module not found: {str(e)}")
                state["result"] = None
                state["success"] = False
                state["error_message"] = f"Required module not found: {str(e)}"
                state["error_trace"] = traceback.format_exc()
            except Exception as e:
                logger.error(f"Code execution failed: {str(e)}")
                state["result"] = None
                state["success"] = False
                state["error_message"] = f"Code execution failed: {str(e)}"
                state["error_trace"] = traceback.format_exc()
        else:
            state["result"] = None
            state["success"] = False
            state["error_message"] = f"Unsupported language: {state['language']}"
            state["error_trace"] = traceback.format_exc()
            logger.error(state["error_message"])
    except Exception as e:
        logger.error(f"Execution agent failed: {str(e)}")
        state["result"] = None
        state["success"] = False
        state["error_message"] = f"Execution agent failed: {str(e)}"
        state["error_trace"] = traceback.format_exc()
    return state
