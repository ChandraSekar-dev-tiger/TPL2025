import asyncio
from core.session_manager import create_session_id, get_session_state, save_session_state
from pipelines.pipeline import run_agent_pipeline

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

if __name__ == "__main__":
    async def run_test():
        test_input = {
            "query": "Show me sales by category last month",
            "session_id": "test_session_001"
        }

        result = await query_agent(test_input)
        print("=== Test Output ===")
        print(result)

    asyncio.run(run_test())
