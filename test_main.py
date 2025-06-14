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

    # Run the pipeline with session-aware state
    output = await run_agent_pipeline(user_query, session_state)

    # Save new state after execution
    new_session_state = output.get("session_state", {})
    save_session_state(session_id, new_session_state)

    return {
        "session_id": session_id,
        "result": output.get("report", {"report_text": "No report generated."})
    }

async def run_test():
    test_input = {
        "query": "Show me total sales by category",
        "session_id": "test_session_001"
    }
    
    logger.info("Starting test with query: %s", test_input["query"])
    result = await query_agent(test_input)
    logger.info("Test completed with result: %s", result)
    print("\n=== Test Output ===")
    print(result)

if __name__ == "__main__":
    asyncio.run(run_test())
