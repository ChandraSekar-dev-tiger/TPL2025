from typing import TypedDict, Optional
from core.execute_code_tool import execute_code

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
    result = execute_code(state["code"], state["language"])
    if result.startswith("Execution failed"):
        state["success"] = False
        state["error_message"] = result
        state["result"] = None
    else:
        state["success"] = True
        state["result"] = result
        state["error_message"] = None
    return state
