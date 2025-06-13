import logging
from langgraph.graph import StateGraph, END

from agents.intent_agent import intent_recognition_agent, IntentState
from agents.retrieval_agent import retrieval_agent, RetrievalState
from agents.codegen_agent import code_generation_agent, CodeGenState
from agents.execution_agent import execution_agent, ExecutionState
from agents.interpretation_agent import interpretation_agent, InterpretationState
from agents.reporting_agent import reporting_agent, ReportingState

from core.config import ROLE
import json

logger = logging.getLogger(__name__)

def run_agent_pipeline(user_query: str, user_role: str = ROLE, metadata: dict = None) -> dict:
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

    # Run pipeline stepwise manually, passing state dictionaries between steps

    # Step 1: Intent Recognition
    state = intent_recognition_agent(intent_state)
    if state["intent"] == "unknown":
        return {"report_text": "Sorry, I could not understand your query."}

    # Step 2: Retrieval
    retrieval_input = {
        "query": state["query"],
        "intent": state["intent"],
        "confidence": state["confidence"],
        "filtered_metadata": None
    }
    retrieval_output = retrieval_agent(retrieval_input, metadata, user_role)
    retrieval_output["query"] = state["query"]
    retrieval_output["intent"] = state["intent"]
    retrieval_output["confidence"] = state["confidence"]

    # Step 3: Code Generation
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

    # Step 4: Execution
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

    # Step 5: Interpretation
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

    # Step 6: Reporting
    reporting_input = {
        "query": state["query"],
        "insight": interpretation_output["insight"],
        "result": execution_output["result"],
        "report_text": None
    }
    reporting_output = reporting_agent(reporting_input)

    return reporting_output
