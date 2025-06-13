from typing import TypedDict, Optional, Any
from langgraph.graph import StateGraph, END

from agents.intent_agent import intent_recognition_agent, IntentState
from agents.retrieval_agent import retrieval_agent
from agents.codegen_agent import code_generation_agent
from agents.execution_agent import execution_agent
from agents.interpretation_agent import interpretation_agent
from agents.reporting_agent import reporting_agent


# Define the shared state schema across agents
class AgentState(TypedDict):
    query: str
    session_id: Optional[str]
    session_state: dict
    report: Optional[dict]


# Your main agent pipeline function
async def run_agent_pipeline(user_query: str, session_state: dict) -> dict:
    graph = StateGraph(AgentState)  # ✅ REQUIRED in LangGraph >= 0.0.38

    # Extract or initialize states from session_state dictionary
    intent_state: IntentState = session_state.get("intent_state") or {
        "query": user_query,
        "intent": None,
        "confidence": None
    }

    retrieval_state = session_state.get("retrieval_state") or {
        "query": user_query,
        "intent": "",
        "confidence": 0.0,
        "filtered_metadata": None
    }

    codegen_state = session_state.get("codegen_state") or {
        "query": user_query,
        "intent": "",
        "confidence": 0.0,
        "filtered_metadata": {},
        "code": None,
        "language": None
    }

    execution_state = session_state.get("execution_state") or {
        "query": user_query,
        "intent": "",
        "confidence": 0.0,
        "code": "",
        "language": "",
        "result": None,
        "success": None,
        "error_message": None
    }

    interpretation_state = session_state.get("interpretation_state") or {
        "query": user_query,
        "intent": "",
        "confidence": 0.0,
        "code": "",
        "language": "",
        "result": None,
        "insight": None
    }

    reporting_state = session_state.get("reporting_state") or {
        "query": user_query,
        "insight": "",
        "result": None,
        "report_text": None
    }

    # Step-by-step execution, no LangGraph runtime for now
    intent_state = intent_recognition_agent(intent_state)
    if intent_state["intent"] == "unknown":
        return {"report": {"report_text": "Sorry, I could not understand your query."}}

    retrieval_state = retrieval_agent({
        "query": user_query,
        "intent": intent_state["intent"],
        "confidence": intent_state["confidence"],
        "filtered_metadata": None,
    })

    codegen_state = code_generation_agent({
        "query": user_query,
        "intent": intent_state["intent"],
        "confidence": intent_state["confidence"],
        "filtered_metadata": retrieval_state.get("filtered_metadata", {}),
        "code": None,
        "language": None,
    })

    if not codegen_state.get("code"):
        return {"report": {"report_text": "Failed to generate code for your query."}}

    execution_state = execution_agent({
        "query": user_query,
        "intent": intent_state["intent"],
        "confidence": intent_state["confidence"],
        "code": codegen_state["code"],
        "language": codegen_state["language"],
        "result": None,
        "success": None,
        "error_message": None,
    })

    if not execution_state.get("success"):
        return {"report": {"report_text": f"Execution error: {execution_state.get('error_message', 'Unknown error')}"}}

    interpretation_state = interpretation_agent({
        "query": user_query,
        "intent": intent_state["intent"],
        "confidence": intent_state["confidence"],
        "code": codegen_state["code"],
        "language": codegen_state["language"],
        "result": execution_state["result"],
        "insight": None,
    })

    reporting_state = reporting_agent({
        "query": user_query,
        "insight": interpretation_state["insight"],
        "result": execution_state["result"],
        "report_text": None,
    })

    # Update session state
    updated_session_state = {
        "intent_state": intent_state,
        "retrieval_state": retrieval_state,
        "codegen_state": codegen_state,
        "execution_state": execution_state,
        "interpretation_state": interpretation_state,
        "reporting_state": reporting_state,
    }

    return {
        "report": reporting_state.get("report_text", "No report_text"),
        "session_state": updated_session_state
    }
