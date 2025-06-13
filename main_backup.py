# agent.py

import os
import json
import traceback
import logging
from typing import TypedDict, Optional, Dict, Any

from langchain.chat_models import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --- Config ---
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
EMBEDDING_MODEL = os.getenv("AZURE_EMBEDDING_MODEL")
DATA_PATH = "/mnt/data/delta/"
ROLE = "non_clinical_staff"  # In prod, derive from user session

# --- Load Metadata ---
with open("./metadata_with_roles.json") as f:
    metadata = json.load(f)

def filter_metadata_by_role(metadata: dict, role: str) -> dict:
    filtered = {}
    for sheet, cols in metadata.items():
        allowed = [col for col in cols if role in col.get("access_roles", [])]
        if allowed:
            filtered[sheet] = allowed
    return filtered

role_filtered_metadata = filter_metadata_by_role(metadata, ROLE)

# --- LLM Model ---
llm = AzureChatOpenAI(
    deployment_name=AZURE_DEPLOYMENT_NAME,
    temperature=0.2,
    model_name="gpt-4"
)

# --- TypedDicts for states ---

class IntentState(TypedDict):
    query: str
    intent: Optional[str]
    confidence: Optional[float]

class RetrievalState(TypedDict):
    query: str
    intent: str
    confidence: float
    filtered_metadata: Optional[dict]

class CodeGenState(TypedDict):
    query: str
    intent: str
    confidence: float
    filtered_metadata: dict
    code: Optional[str]
    language: Optional[str]

class ExecutionState(TypedDict):
    query: str
    intent: str
    confidence: float
    code: str
    language: str
    result: Optional[Any]
    success: Optional[bool]
    error_message: Optional[str]

class InterpretationState(TypedDict):
    query: str
    intent: str
    confidence: float
    code: str
    language: str
    result: Any
    insight: Optional[str]

class ReportingState(TypedDict):
    query: str
    insight: str
    result: Any
    report_text: Optional[str]

# --- Tools ---

@tool
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

# --- Prompt Templates ---

intent_prompt_template = ChatPromptTemplate.from_template(
    """
You are an intent classifier for healthcare queries.
Classify the intent of this user query into one of the categories:
- aggregate_query
- trend_analysis
- comparison
- general_query
- unknown

User query:
{query}

Return only JSON with keys 'intent' and 'confidence' (0-1).
"""
)

retrieval_prompt_template = ChatPromptTemplate.from_template(
    """
You are a retrieval agent.
Based on the intent '{intent}' and role-based metadata, determine the relevant data fields and tables.

Metadata (filtered by role):
{filtered_metadata}

User query:
{query}

Return JSON of relevant metadata keys and descriptions.
"""
)

codegen_prompt_template = ChatPromptTemplate.from_template(
    """
You are a healthcare data code generation agent.
Using the intent '{intent}' and filtered metadata:
{filtered_metadata}

Generate {language} code that answers the user query:
{query}

Return only the code block without explanation.
"""
)

interpretation_prompt_template = ChatPromptTemplate.from_template(
    """
You are an AI assistant that analyzes the result of a healthcare data query with intent '{intent}'.
Provide a concise, actionable insight in natural language based on this result:

{result}
"""
)

# --- Agent Functions ---

def intent_recognition_agent(state: IntentState) -> IntentState:
    try:
        response = llm.invoke(intent_prompt_template.format_prompt(query=state["query"]))
        # parse JSON response safely
        import json as js
        j = js.loads(response.content)
        state["intent"] = j.get("intent", "unknown")
        state["confidence"] = j.get("confidence", 0.0)
        logger.info(f"Intent recognized: {state['intent']} with confidence {state['confidence']}")
        return state
    except Exception as e:
        logger.error(f"Intent recognition failed: {e}")
        state["intent"] = "unknown"
        state["confidence"] = 0.0
        return state

def retrieval_agent(state: RetrievalState) -> RetrievalState:
    try:
        # For now, just reuse role-filtered metadata, optionally could call retrieval LLM
        state["filtered_metadata"] = role_filtered_metadata
        return state
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        state["filtered_metadata"] = {}
        return state

def code_generation_agent(state: CodeGenState) -> CodeGenState:
    try:
        prompt_text = codegen_prompt_template.format_prompt(
            intent=state["intent"],
            filtered_metadata=json.dumps(state["filtered_metadata"], indent=2),
            query=state["query"],
            language="PySpark"
        )
        response = llm.invoke(prompt_text)
        code = response.content.strip()
        state["code"] = code
        state["language"] = "pyspark"
        logger.info("Code generation successful.")
        return state
    except Exception as e:
        logger.error(f"Code generation failed: {e}")
        state["code"] = None
        state["language"] = None
        return state

def execution_agent(state: ExecutionState) -> ExecutionState:
    try:
        result = execute_code.invoke({"code": state["code"], "language": state["language"]})
        # result is string, you can parse if you want
        state["result"] = result
        state["success"] = True
        state["error_message"] = None
        logger.info("Code execution successful.")
        return state
    except Exception as e:
        err = traceback.format_exc()
        logger.error(f"Execution error: {err}")
        state["result"] = None
        state["success"] = False
        state["error_message"] = str(e)
        return state

def interpretation_agent(state: InterpretationState) -> InterpretationState:
    try:
        prompt_text = interpretation_prompt_template.format_prompt(
            intent=state["intent"],
            result=state["result"]
        )
        response = llm.invoke(prompt_text)
        insight = response.content.strip()
        state["insight"] = insight
        logger.info("Interpretation (insight) generated.")
        return state
    except Exception as e:
        logger.error(f"Interpretation failed: {e}")
        state["insight"] = "Insight generation failed."
        return state

def reporting_agent(state: ReportingState) -> ReportingState:
    try:
        report = f"Actionable Insight:\n{state['insight']}\n\nRaw Result:\n{str(state['result'])[:1000]}"
        state["report_text"] = report
        logger.info("Reporting complete.")
        return state
    except Exception as e:
        logger.error(f"Reporting failed: {e}")
        state["report_text"] = "Failed to generate report."
        return state

# --- Graph Pipeline ---

# Define states per step with relevant keys

def run_agent_pipeline(user_query: str, user_role: str = ROLE) -> dict:
    graph = StateGraph()

    # Initialize states
    intent_state: IntentState = {"query": user_query, "intent": None, "confidence": None}
    retrieval_state: RetrievalState = {"query": user_query, "intent": "", "confidence": 0.0, "filtered_metadata": None}
    codegen_state: CodeGenState = {"query": user_query, "intent": "", "confidence": 0.0, "filtered_metadata": {}, "code": None, "language": None}
    execution_state: ExecutionState = {"query": user_query, "intent": "", "confidence": 0.0, "code": "", "language": "", "result": None, "success": None, "error_message": None}
    interpretation_state: InterpretationState = {"query": user_query, "intent": "", "confidence": 0.0, "code": "", "language": "", "result": None, "insight": None}
    reporting_state: ReportingState = {"query": user_query, "insight": "", "result": None, "report_text": None}

    # Add nodes
    graph.add_node("intent_recognition", intent_recognition_agent)
    graph.add_node("retrieval", retrieval_agent)
    graph.add_node("code_generation", code_generation_agent)
    graph.add_node("execution", execution_agent)
    graph.add_node("interpretation", interpretation_agent)
    graph.add_node("reporting", reporting_agent)
    graph.set_entry_point("intent_recognition")

    # Add edges
    graph.add_edge("intent_recognition", "retrieval")
    graph.add_edge("retrieval", "code_generation")
    graph.add_edge("code_generation", "execution")
    graph.add_edge("execution", "interpretation")
    graph.add_edge("interpretation", "reporting")
    graph.add_edge("reporting", END)

    # Compose state passing
    # The agent graph invokes each node with the last node's returned state dict
    # We'll need to chain states properly, so we wrap each node to inject/merge state

    def merge_states(prev_state: dict, new_state: dict) -> dict:
        # merge dicts, with new_state overwriting prev_state keys
        combined = prev_state.copy()
        combined.update(new_state)
        return combined

    state = intent_state

    # Intent Recognition
    state = intent_recognition_agent(state)  # adds intent and confidence
    if state["intent"] == "unknown":
        return {"report_text": "Sorry, I could not understand your query."}

    # Retrieval
    retrieval_input = {
        "query": state["query"],
        "intent": state["intent"],
        "confidence": state["confidence"],
        "filtered_metadata": None
    }
    retrieval_output = retrieval_agent(retrieval_input)
    retrieval_output["query"] = state["query"]
    retrieval_output["intent"] = state["intent"]
    retrieval_output["confidence"] = state["confidence"]

    # Code Generation
    codegen_input = {
        "query": state["query"],
        "intent": state["intent"],
        "confidence": state["confidence"],
        "filtered_metadata": retrieval_output["filtered_metadata"],
        "code": None,
        "language": None
    }
    codegen_output = code_generation_agent(codegen_input)
    if not codegen_output["code"]:
        return {"report_text": "Failed to generate code for your query."}

    # Execution
    execution_input = {
        "query": state["query"],
        "intent": state["intent"],
        "confidence": state["confidence"],
        "code": codegen_output["code"],
        "language": codegen_output["language"],
        "result": None,
        "success": None,
        "error_message": None
    }
    execution_output = execution_agent(execution_input)
    if not execution_output["success"]:
        return {"report_text": f"Execution error: {execution_output['error_message']}"}

    # Interpretation
    interpretation_input = {
        "query": state["query"],
        "intent": state["intent"],
        "confidence": state["confidence"],
        "code": codegen_output["code"],
        "language": codegen_output["language"],
        "result": execution_output["result"],
        "insight": None
    }
    interpretation_output = interpretation_agent(interpretation_input)

    # Reporting
    reporting_input = {
        "query": state["query"],
        "insight": interpretation_output["insight"],
        "result": execution_output["result"],
        "report_text": None
    }
    reporting_output = reporting_agent(reporting_input)

    return reporting_output


# --- Example usage ---

if __name__ == "__main__":
    query = "What is the patient readmission rate for cardiology in the last quarter?"
    output = run_agent_pipeline(query, ROLE)
    print("\n=== Final Report ===")
    print(output.get("report_text", "No report generated."))
