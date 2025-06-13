from typing import Dict, Any
from agents.intent_agent import intent_recognition_agent, IntentState
from agents.retrieval_agent import retrieval_agent, RetrievalState
from agents.codegen_agent import code_generation_agent, CodeGenState
from agents.execution_agent import execution_agent, ExecutionState
from agents.interpretation_agent import interpretation_agent, InterpretationState
from agents.reporting_agent import reporting_agent, ReportingState

def run_agent_pipeline(user_query: str, user_role: str = "non_clinical_staff") -> Dict[str, Any]:
    # Intent recognition
    intent_state: IntentState = {"query": user_query, "intent": None, "confidence": None}
    intent_state = intent_recognition_agent(intent_state)
    if intent_state["intent"] == "unknown":
        return {"report_text": "Sorry, I could not understand your query."}

    # Retrieval
    retrieval_state: RetrievalState = {
        "query": user_query,
        "intent": intent_state["intent"],
        "confidence": intent_state["confidence"],
        "filtered_metadata": None,
    }
    retrieval_state = retrieval_agent(retrieval_state)

    # Code Generation
    codegen_state: CodeGenState = {
        "query": user_query,
        "intent": intent_state["intent"],
        "confidence": intent_state["confidence"],
        "filtered_metadata": retrieval_state["filtered_metadata"],
        "code": None,
        "language": None,
    }
    codegen_state = code_generation_agent(codegen_state)
    if not codegen_state["code"]:
        return {"report_text": "Failed to generate code for your query."}

    # Execution
    execution_state: ExecutionState = {
        "query": user_query,
        "intent": intent_state["intent"],
        "confidence": intent_state["confidence"],
        "code": codegen_state["code"],
        "language": codegen_state["language"],
        "result": None,
        "success": None,
        "error_message": None,
    }
    execution_state = execution_agent(execution_state)
    if not execution_state["success"]:
        return {"report_text": f"Execution error: {execution_state['error_message']}"}

    # Interpretation
    interpretation_state: InterpretationState = {
        "query": user_query,
        "intent": intent_state["intent"],
        "confidence": intent_state["confidence"],
        "code": codegen_state["code"],
        "language": codegen_state["language"],
        "result": execution_state["result"],
        "insight": None,
    }
    interpretation_state = interpretation_agent(interpretation_state)

    # Reporting
    reporting_state: ReportingState = {
        "query": user_query,
        "insight": interpretation_state["insight"],
        "result": execution_state["result"],
        "report_text": None,
    }
    reporting_state = reporting_agent(reporting_state)

    return reporting_state
