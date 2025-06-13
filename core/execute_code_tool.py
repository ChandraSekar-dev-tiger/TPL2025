import traceback
import logging

logger = logging.getLogger(__name__)

def execute_code(code: str, language: str = "sql") -> str:
    """
    Execute SQL (via DuckDB) or PySpark code safely.
    Returns output string or error message.
    """
    try:
        if language == "sql":
            import duckdb
            conn = duckdb.connect()
            conn.execute("INSTALL httpfs; LOAD httpfs;")
            result = conn.execute(code).fetchall()
            return str(result)
        elif language == "pyspark":
            from pyspark.sql import SparkSession
            spark = SparkSession.builder.appName("AgentExecutor").getOrCreate()
            exec_globals = {"spark": spark}
            exec_locals = {}
            exec(code, exec_globals, exec_locals)
            return str(exec_locals.get("result", "PySpark code executed."))
        else:
            return "Unsupported language. Use 'sql' or 'pyspark'."
    except Exception as e:
        err = traceback.format_exc()
        logger.error(f"Code execution error: {err}")
        return f"Execution failed: {str(e)}"
