import asyncio
import logging
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from core.session_manager import create_session_id, get_session_state, save_session_state
from core.logging_config import setup_logging
from pipelines.pipeline import run_agent_pipeline

# Set up logging
setup_logging(log_level="DEBUG")

logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/query")
async def query_agent(request: Request):
    data = await request.json()
    user_query = data.get("query", "")
    session_id = data.get("session_id")

    if not user_query:
        return JSONResponse({"error": "Missing query parameter"}, status_code=400)

    # Create new session if missing
    if not session_id:
        session_id = create_session_id()

    session_state = get_session_state(session_id) or {}
    if session_state:
        print(f"[LOAD] Session found: {session_id}")
        print(session_state)

    # Run pipeline with session
    output = await run_agent_pipeline(user_query, session_state)

    # Save updated session
    new_session_state = output.get("session_state", {})
    save_session_state(session_id, new_session_state)
    print(f"[SAVE] Session updated: {session_id}")

    # Return response with session_id so client can save it
    response = {
        "session_id": session_id,
        "result": output.get("report", {"report_text": "No report generated."})
    }

    return JSONResponse(content=jsonable_encoder(response))

async def main():
    while True:
        try:
            user_input = input("\nEnter your query (or 'quit' to exit): ")
            if user_input.lower() == 'quit':
                break

            result = await query_agent({"query": user_input})
            print("\nResult:")
            print(result["result"]["report_text"])

        except Exception as e:
            logger.error("Error processing query: %s", str(e))
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
