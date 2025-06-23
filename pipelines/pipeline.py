import logging
import traceback
from typing import Any, Optional, TypedDict, Union

from langgraph.graph import END, StateGraph

from agents.codegen_agent import CodegenState, code_generation_agent
from agents.execution_agent import ExecutionState, execution_agent
from agents.intent_agent import IntentState, intent_recognition_agent
from agents.interpretation_agent import InterpretationState, interpretation_agent
from agents.logical_check_agent import LogicalCheckState, logical_check_agent
from agents.reporting_agent import ReportingState, reporting_agent
from agents.retrieval_agent import RetrievalState, retrieval_agent

logger = logging.getLogger(__name__)


# Define the combined state schema that includes all agent states
class AgentState(TypedDict):
    query: str
    user_role: str
    session_id: Optional[str]
    relevance: Optional[int]
    reasoning: Optional[str]
    filtered_metadata: Optional[dict]
    code: Optional[str]
    language: Optional[str]
    result: Optional[Any]
    success: Optional[bool]
    error_message: Optional[str]
    insight: Optional[str]
    report_text: Optional[str]
    error_trace: Optional[str]
    current_node: Optional[str]
    codegen_attempts: Optional[int]  # Track number of code generation attempts
    max_codegen_attempts: Optional[int]  # Maximum number of attempts allowed
    enable_logical_check: Optional[bool]  # Flag to enable/disable logical check
    logical_errors: Optional[list]  # List of logical errors found
    syntax_errors: Optional[list]  # List of syntax errors found


def should_continue(state: AgentState) -> Union[str, bool]:
    """Determine the next node based on the current state."""
    try:
        current_node = state.get("current_node", "intent_recognition")

        if current_node == "intent_recognition":
            if state.get("relevance", 0) == 0:
                logger.warning("Non-healthcare query detected")
                return "error_reporting"
            return True

        elif current_node == "retrieval":
            if not state.get("filtered_metadata"):
                logger.warning("No metadata retrieved")
                return "error_reporting"
            return True

        elif current_node == "code_generation":
            attempts = state.get("codegen_attempts", 0)
            max_attempts = state.get("max_codegen_attempts", 3)

            # If we have an error message or no code, and we haven't exceeded max attempts
            if (
                state.get("error_message") or not state.get("code")
            ) and attempts < max_attempts:
                logger.warning(
                    f"Code generation failed on attempt {attempts}, retrying..."
                )
                return "code_generation"  # Retry code generation
            elif attempts >= max_attempts:
                logger.error("Maximum code generation attempts reached")
                return "error_reporting"
            return True

        elif current_node == "logical_check":
            if state.get("enable_logical_check", False):
                if state.get("logical_errors"):
                    attempts = state.get("codegen_attempts", 0)
                    max_attempts = state.get("max_codegen_attempts", 3)
                    if attempts < max_attempts:
                        logger.warning(
                            "Logical errors found, returning to code generation"
                        )
                        return "code_generation"
                    else:
                        logger.error("Maximum code generation attempts reached")
                        return "error_reporting"
            return True

        elif current_node == "execution":
            if not state.get("success", True):
                error_msg = state.get("error_message", "")
                syntax_errors = state.get("syntax_errors", [])

                # Check for syntax errors in both error message and syntax_errors list
                has_syntax_error = (
                    any(
                        err.get("type") in ["SyntaxError", "IndentationError"]
                        for err in syntax_errors
                    )
                    or "SyntaxError" in error_msg
                    or "IndentationError" in error_msg
                )

                if has_syntax_error:
                    attempts = state.get("codegen_attempts", 0)
                    max_attempts = state.get("max_codegen_attempts", 3)
                    if attempts < max_attempts:
                        logger.warning(
                            "Syntax error found, returning to code generation"
                        )
                        return "code_generation"
                    else:
                        logger.error("Maximum code generation attempts reached")
                        return "error_reporting"
                else:
                    logger.warning(f"Execution failed: {error_msg}")
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

        if state.get("relevance", 0) == 0:
            reasoning = state.get("reasoning", "")
            state["report_text"] = reasoning
            logger.info(f"Non-healthcare query report: {reasoning}")
            return state
        elif not state.get("code"):
            error_msg = "Failed to generate code for your query."
            state["report_text"] = f"Error: {error_msg}"
        else:
            state["report_text"] = f"Error: {error_msg}"
            if error_trace:
                state["report_text"] += f"\n\nTechnical Details:\n{error_trace}"

        logger.error(f"Error report generated: {error_msg}")
        return state
    except Exception as e:
        logger.error(f"Error in create_error_report: {str(e)}")
        state["report_text"] = f"Critical error in error reporting: {str(e)}"
        state["error_trace"] = traceback.format_exc()
        return state


async def run_agent_pipeline(
    user_query: str,
    user_role: str,
    session_state: dict,
    max_codegen_attempts: int = 3,
    enable_logical_check: bool = False,
) -> dict:
    try:
        # Initialize the graph with our combined state schema
        graph = StateGraph(AgentState)

        # Add nodes for each agent
        graph.add_node("intent_recognition", intent_recognition_agent)
        graph.add_node("retrieval", retrieval_agent)
        graph.add_node(
            "code_generation", lambda state: code_generation_agent(state, user_role)
        )
        graph.add_node("logical_check", logical_check_agent)
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
            {True: "retrieval", "error_reporting": "error_reporting"},
        )

        graph.add_conditional_edges(
            "retrieval",
            should_continue,
            {True: "code_generation", "error_reporting": "error_reporting"},
        )

        # Add edges for code generation with retry support
        graph.add_conditional_edges(
            "code_generation",
            should_continue,
            {
                True: "logical_check" if enable_logical_check else "execution",
                "code_generation": "code_generation",  # Add self-loop for retries
                "error_reporting": "error_reporting",
            },
        )

        if enable_logical_check:
            graph.add_conditional_edges(
                "logical_check",
                should_continue,
                {
                    True: "execution",
                    "code_generation": "code_generation",  # Add edge back to code generation
                    "error_reporting": "error_reporting",
                },
            )

        graph.add_conditional_edges(
            "execution",
            should_continue,
            {
                True: "interpretation",
                "code_generation": "code_generation",  # Add edge back to code generation for retries
                "error_reporting": "error_reporting",
            },
        )

        graph.add_edge("interpretation", "reporting")
        graph.add_edge("reporting", END)
        graph.add_edge("error_reporting", END)

        # Initialize the state with session state values
        initial_state = {
            "query": user_query,
            "user_role": user_role,
            "session_id": session_state.get("session_id"),
            "current_node": "intent_recognition",
            "relevance": session_state.get("relevance", 0),
            "reasoning": session_state.get("reasoning", ""),
            "filtered_metadata": session_state.get("filtered_metadata"),
            "code": session_state.get("code"),
            "language": session_state.get("language", "sql"),
            "result": session_state.get("result"),
            "success": session_state.get("success"),
            "error_message": session_state.get("error_message"),
            "insight": session_state.get("insight"),
            "report_text": session_state.get("report_text"),
            "error_trace": session_state.get("error_trace"),
            "codegen_attempts": session_state.get(
                "codegen_attempts", 0
            ),  # Preserve attempts from session
            "max_codegen_attempts": max_codegen_attempts,
            "enable_logical_check": enable_logical_check,
            "logical_errors": session_state.get(
                "logical_errors", []
            ),  # Preserve logical errors
            "syntax_errors": session_state.get(
                "syntax_errors", []
            ),  # Preserve syntax errors
        }

        # Run the graph
        compiled_graph = graph.compile()
        result = await compiled_graph.ainvoke(initial_state)

        # Update session state with the final state
        session_state.update(
            {
                "codegen_attempts": result.get("codegen_attempts", 0),
                "query": result.get("query"),
                "user_role": result.get("user_role"),
                "relevance": result.get("relevance", 0),
                "reasoning": result.get("reasoning", ""),
                "filtered_metadata": result.get("filtered_metadata"),
                "code": result.get("code"),
                "language": result.get("language"),
                "result": result.get("result"),
                "success": result.get("success"),
                "error_message": result.get("error_message"),
                "insight": result.get("insight"),
                "report_text": result.get("report_text"),
                "error_trace": result.get("error_trace"),
                "logical_errors": result.get(
                    "logical_errors", []
                ),  # Preserve logical errors
                "syntax_errors": result.get(
                    "syntax_errors", []
                ),  # Preserve syntax errors
            }
        )

        # Ensure we return the updated session state
        return {
            "report": {
                "report_text": result.get("report_text", "No report generated.")
            },
            "session_state": session_state,  # Return the updated session state
        }

    except Exception as e:
        logger.error(f"Critical error in pipeline: {str(e)}")
        logger.error(f"Error trace: {traceback.format_exc()}")
        return {
            "report": {
                "report_text": f"Critical pipeline error: {str(e)}\n\nTechnical Details:\n{traceback.format_exc()}"
            },
            "session_state": session_state,  # Return the original session state on error
        }
