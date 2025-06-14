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
    syntax_errors: Optional[list]
    current_node: Optional[str]

def execution_agent(state: ExecutionState) -> ExecutionState:
    try:
        if not state.get("code"):
            state["success"] = False
            state["error_message"] = "No code provided for execution"
            state["error_trace"] = traceback.format_exc()
            state["current_node"] = "execution"
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
                
                # Dummy code to simulate syntax error
                # state["error_message"] = "Syntax error: invalid syntax"
                # state["error_trace"] = "Traceback (most recent call last):\n  File \"<string>\", line 1\n    print('Hello World'\n                    ^\nSyntaxError: unexpected EOF while parsing"
                # state["syntax_errors"] = [{
                #     "type": "SyntaxError",
                #     "message": "unexpected EOF while parsing",
                #     "line": 1,
                #     "offset": 20,
                #     "text": "print('Hello World'"
                # }]
                # state["success"] = False
                # state["result"] = None
                # state["current_node"] = "execution"
                # logger.error("Python code execution failed with syntax error")
                # return state  # Return early to prevent further execution


                state["result"] = result
                state["success"] = True
                state["error_message"] = None
                state["error_trace"] = None
                state["syntax_errors"] = []  # Clear syntax errors on success
                state["current_node"] = "execution"
                logger.info("Python code executed successfully")

            except SyntaxError as e:
                logger.error(f"Syntax error in code: {str(e)}")
                state["result"] = None
                state["success"] = False
                state["error_message"] = f"Syntax error: {str(e)}"
                state["error_trace"] = traceback.format_exc()
                # Add syntax error to the list with more details
                error_details = {
                    "type": "SyntaxError",
                    "message": str(e),
                    "line": getattr(e, 'lineno', None),
                    "offset": getattr(e, 'offset', None),
                    "text": getattr(e, 'text', None)
                }
                state["syntax_errors"] = state.get("syntax_errors", []) + [error_details]
            except IndentationError as e:
                logger.error(f"Indentation error in code: {str(e)}")
                state["result"] = None
                state["success"] = False
                state["error_message"] = f"Indentation error: {str(e)}"
                state["error_trace"] = traceback.format_exc()
                # Add indentation error to the list with more details
                error_details = {
                    "type": "IndentationError",
                    "message": str(e),
                    "line": getattr(e, 'lineno', None),
                    "offset": getattr(e, 'offset', None),
                    "text": getattr(e, 'text', None)
                }
                state["syntax_errors"] = state.get("syntax_errors", []) + [error_details]
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
