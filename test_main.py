import asyncio
import logging
from core.session_manager import create_session_id, get_session_state, save_session_state
from core.logging_config import setup_logging
from pipelines.pipeline import run_agent_pipeline

# Set up logging
setup_logging(log_level="DEBUG")

logger = logging.getLogger(__name__)

async def query_agent(data: dict):
    user_query = data.get("query", "")
    session_id = data.get("session_id")

    if not user_query:
        raise ValueError("Missing 'query' in request data")

    # Create a session if not provided
    if not session_id:
        session_id = create_session_id()

    # Retrieve previous session state or start fresh
    session_state = get_session_state(session_id) or {}

    # Run the pipeline with session-aware state and enable logical checks
    output = await run_agent_pipeline(
        user_query, 
        session_state,
        max_codegen_attempts=3,
        enable_logical_check=True  # Enable logical checks
    )

    # Save new state after execution
    new_session_state = output.get("session_state", {})
    save_session_state(session_id, new_session_state)

    return {
        "session_id": session_id,
        "result": {
            "report": output.get("report", {"report_text": "No report generated."}),
            "session_state": new_session_state
        }
    }

async def test_codegen_retries():
    # Test case 1: Query that should trigger codegen retries
    test_input = {
        "query": "Generate code with logical error",  # This should trigger retries
        "session_id": "test_session_retry_001"
    }
    
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
    
    # Add assertion to verify retries
    assert codegen_attempts > 0, "Expected at least one codegen attempt"
    assert codegen_attempts <= 3, "Expected at most 3 codegen attempts"

async def run_tests():
    # Run the retry test
    await test_codegen_retries()

if __name__ == "__main__":
    asyncio.run(run_tests())