import asyncio
import logging
from guardrails import apply_guardrails 
from core.logging_config import setup_logging
from core.session_manager import (
    create_session_id,
    get_session_state,
    save_session_state,
)
from pipelines.pipeline import run_agent_pipeline

# Set up logging
setup_logging(log_level="INFO")

logger = logging.getLogger(__name__)


async def query_agent(data: dict):
    user_query = data.get("query", "")
    user_role = data.get("user_role", "")
    session_id = data.get("session_id")

    if not user_query:
        raise ValueError("Missing 'query' in request data")

    if user_role not in ["managers", "non_clinical_staff", "administrative_staff"]:
        raise ValueError(
            "Invalid 'user_role'. Must be one of: managers, non_clinical_staff, administrative_staff"
        )

    # Create a session if not provided
    if not session_id:
        session_id = create_session_id()

    # Retrieve previous session state or start fresh
    session_state = get_session_state(session_id) or {}
    # apply guardrails
    table_name = session_state.get("current_table", "")  # If available
    generated_code = session_state.get("code", "")       # If previously stored

    violations = apply_guardrails(
        query=user_query,
        role=user_role,
        intent=session_state.get("intent", ""),
        table=table_name,
        code=generated_code,
    )
    if violations:
        logger.warning(f"Query blocked due to guardrail violations: {violations}")
        return {
            "session_id": session_id,
            "result": {
                "report": {
                    "report_text": "Your query was blocked due to policy violations.",
                    "violations": violations
                },
                "session_state": session_state,
            },
        }

    # Run the pipeline with session-aware state and enable logical checks
    output = await run_agent_pipeline(
        user_query,
        user_role,
        session_state,
        max_codegen_attempts=3,
        enable_logical_check=False,  # Enable logical checks True, False
    )

    # Save new state after execution
    new_session_state = output.get("session_state", {})
    save_session_state(session_id, new_session_state)

    return {
        "session_id": session_id,
        "result": {
            "report": output.get("report", {"report_text": "No report generated."}),
            "session_state": new_session_state,
        },
    }


async def test_codegen_retries(test_input):

    logger.info("Starting retry test with query: %s", test_input["query"])
    result = await query_agent(test_input)

    # Get the session state from the result
    session_state = result.get("result", {}).get("session_state", {})
    # logger.debug("Retrieved session state: %s", session_state)

    codegen_attempts = session_state.get("codegen_attempts", 0)
    # logger.info("Test completed with result: %s", result)
    logger.info("Number of codegen attempts: %d", codegen_attempts)

    print("\n=== Retry Test Output ===")
    # Extract and print only the markdown text from the report
    report_text = result.get("result", {}).get("report", {}).get("report_text", "")
    if "Markdown Report: messages=" in report_text:
        # Extract the content from the HumanMessage
        content_start = report_text.find("content='") + 9
        content_end = report_text.find("'", content_start)
        if content_start > 8 and content_end > content_start:
            report_text = report_text[content_start:content_end]
    print(f"Report: {report_text}")
    print(f"Number of codegen attempts: {codegen_attempts}")

    return {"result": {"report": report_text, "code": "SELECT * FROM TABLE LIMIT 10;"}}

    # # Add assertion to verify retries
    # assert codegen_attempts > 0, "Expected at least one codegen attempt"
    # assert codegen_attempts <= 3, "Expected at most 3 codegen attempts"


async def run_tests(input_query=None):
    # Test case 1: Query that should trigger codegen retries
    if input_query is None:
        test_input = {
            "query": "number of patients in emrgency ward",  # This should trigger retries
            "user_role": "non_clinical_staff",  # Valid user role
            "session_id": "test_session_retry_001",
        }
    else:
        test_input = input_query
    # Run the retry test
    await test_codegen_retries(test_input)


if __name__ == "__main__":
    asyncio.run(run_tests())
