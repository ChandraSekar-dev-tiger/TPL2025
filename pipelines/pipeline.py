from typing import TypedDict, Optional, Any, Union
from langgraph.graph import StateGraph, END
import logging
import traceback

from agents.intent_agent import intent_recognition_agent, IntentState
from agents.retrieval_agent import retrieval_agent, RetrievalState
from agents.codegen_agent import code_generation_agent, CodegenState
from agents.execution_agent import execution_agent, ExecutionState
from agents.interpretation_agent import interpretation_agent, InterpretationState
from agents.reporting_agent import reporting_agent, ReportingState

logger = logging.getLogger(__name__)

# Define the combined state schema that includes all agent states
class AgentState(TypedDict):
    query: str
    session_id: Optional[str]
    intent: Optional[str]
    confidence: Optional[float]
    filtered_metadata: Optional[dict]
    code: Optional[str]
    language: Optional[str]
    result: Optional[Any]
    success: Optional[bool]
    error_message: Optional[str]
    insight: Optional[str]
    report_text: Optional[str]
    error_trace: Optional[str]  # Added for detailed error tracking
    current_node: Optional[str]

def should_continue(state: AgentState) -> Union[str, bool]:
    """Determine the next node based on the current state."""
    try:
        # Get the current node from the state
        current_node = state.get("current_node", "intent_recognition")
        
        # Different checks based on the current node
        if current_node == "intent_recognition":
            if state.get("intent") == "unknown":
                logger.warning("Unknown intent detected")
                return "error_reporting"
            return True
            
        elif current_node == "retrieval":
            if not state.get("filtered_metadata"):
                logger.warning("No metadata retrieved")
                return "error_reporting"
            return True
            
        elif current_node == "code_generation":
            if not state.get("code"):
                logger.warning("No code generated")
                return "error_reporting"
            return True
            
        elif current_node == "execution":
            if not state.get("success", True):
                logger.warning(f"Operation failed: {state.get('error_message', 'Unknown error')}")
                return "error_reporting"
            return True
            
        return True
    except Exception as e:
        logger.error(f"Error in should_continue: {str(e)}")
        state["error_message"] = f"Error in state transition: {str(e)}"
        state["error_trace"] = traceback.format_exc()
        return "error_reporting"

def create_error_report(state: AgentState) -> AgentState:
    """Generate an error report when something goes wrong."""
    try:
        error_msg = state.get("error_message", "Unknown error occurred")
        error_trace = state.get("error_trace", "")
        
        if state.get("intent") == "unknown":
            error_msg = "Sorry, I could not understand your query."
        elif not state.get("code"):
            error_msg = "Failed to generate code for your query."
        
        report = f"Error: {error_msg}"
        if error_trace:
            report += f"\n\nTechnical Details:\n{error_trace}"
        
        state["report_text"] = report
        logger.error(f"Error report generated: {error_msg}")
        return state
    except Exception as e:
        logger.error(f"Error in create_error_report: {str(e)}")
        state["report_text"] = f"Critical error in error reporting: {str(e)}"
        state["error_trace"] = traceback.format_exc()
        return state

async def run_agent_pipeline(user_query: str, session_state: dict) -> dict:
    try:
        # Initialize the graph with our combined state schema
        graph = StateGraph(AgentState)

        # Add nodes for each agent
        graph.add_node("intent_recognition", intent_recognition_agent)
        graph.add_node("retrieval", retrieval_agent)
        graph.add_node("code_generation", code_generation_agent)
        graph.add_node("execution", execution_agent)
        graph.add_node("interpretation", interpretation_agent)
        graph.add_node("reporting", reporting_agent)
        graph.add_node("error_reporting", create_error_report)

        # Set the entry point
        graph.set_entry_point("intent_recognition")

        # Add edges with conditional routing
        graph.add_conditional_edges(
            "intent_recognition",
            should_continue,
            {
                True: "retrieval",
                "error_reporting": "error_reporting"
            }
        )
        
        graph.add_conditional_edges(
            "retrieval",
            should_continue,
            {
                True: "code_generation",
                "error_reporting": "error_reporting"
            }
        )

        graph.add_conditional_edges(
            "code_generation",
            should_continue,
            {
                True: "execution",
                "error_reporting": "error_reporting"
            }
        )

        graph.add_conditional_edges(
            "execution",
            should_continue,
            {
                True: "interpretation",
                "error_reporting": "error_reporting"
            }
        )

        graph.add_edge("interpretation", "reporting")
        graph.add_edge("reporting", END)
        graph.add_edge("error_reporting", END)

        # Initialize the state
        initial_state = {
            "query": user_query,
            "session_id": session_state.get("session_id"),
            "current_node": "intent_recognition",  # Add current node tracking
            "intent": None,
            "confidence": None,
            "filtered_metadata": None,
            "code": None,
            "language": None,
            "result": None,
            "success": None,
            "error_message": None,
            "insight": None,
            "report_text": None,
            "error_trace": None
        }

        # Run the graph
        compiled_graph = graph.compile()
        result = await compiled_graph.ainvoke(initial_state)

        # Update session state with the final state
        updated_session_state = {
            "session_id": session_state.get("session_id"),
            "intent_state": {
                "query": result["query"],
                "intent": result["intent"],
                "confidence": result["confidence"]
            },
            "retrieval_state": {
                "query": result["query"],
                "intent": result["intent"],
                "confidence": result["confidence"],
                "filtered_metadata": result["filtered_metadata"]
            },
            "codegen_state": {
                "query": result["query"],
                "intent": result["intent"],
                "confidence": result["confidence"],
                "filtered_metadata": result["filtered_metadata"],
                "code": result["code"],
                "language": result["language"]
            },
            "execution_state": {
                "query": result["query"],
                "intent": result["intent"],
                "confidence": result["confidence"],
                "code": result["code"],
                "language": result["language"],
                "result": result["result"],
                "success": result["success"],
                "error_message": result["error_message"]
            },
            "interpretation_state": {
                "query": result["query"],
                "intent": result["intent"],
                "confidence": result["confidence"],
                "code": result["code"],
                "language": result["language"],
                "result": result["result"],
                "insight": result["insight"]
            },
            "reporting_state": {
                "query": result["query"],
                "insight": result["insight"],
                "result": result["result"],
                "report_text": result["report_text"]
            }
        }

        return {
            "report": {"report_text": result["report_text"]},
            "session_state": updated_session_state
        }
    except Exception as e:
        logger.error(f"Critical error in pipeline: {str(e)}")
        error_trace = traceback.format_exc()
        logger.error(f"Error trace: {error_trace}")
        return {
            "report": {
                "report_text": f"Critical pipeline error: {str(e)}\n\nTechnical Details:\n{error_trace}"
            },
            "session_state": session_state
        }
