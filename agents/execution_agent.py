from typing import TypedDict, Optional, Any
import subprocess
import logging
import traceback
from core.config import (
    DATABRICKS_SERVER_HOSTNAME,
    DATABRICKS_HTTP_PATH,
    DATABRICKS_ACCESS_TOKEN)

import databricks.sql as dbsql
import pandas as pd

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

        if state.get("language", "").lower() == "sql":
            try:
                with dbsql.connect(
                    server_hostname=DATABRICKS_SERVER_HOSTNAME,
                    http_path=DATABRICKS_HTTP_PATH,
                    access_token=DATABRICKS_ACCESS_TOKEN,
                ) as connection:
                    with connection.cursor() as cursor:
                        cursor.execute(state["code"])
                        rows = cursor.fetchall()
                        columns = [desc[0] for desc in cursor.description]
                        df = pd.DataFrame(rows, columns=columns)

                logger.info("SQL executed successfully")

                state["result"] = df
                state["success"] = True
                state["error_message"] = None
                state["error_trace"] = None
                state["syntax_errors"] = []  # Clear syntax errors on success
                state["current_node"] = "execution"
                logger.info("Python code executed successfully")

            except Exception as e:
                logger.error(f"SQL execution failed: {str(e)}")
                state["result"] = None
                state["success"] = False
                state["error_message"] = f"SQL execution failed: {str(e)}"
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
