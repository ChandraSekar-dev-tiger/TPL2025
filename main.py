from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from core.session_manager import create_session_id, get_session_state, save_session_state
from pipelines.pipeline import run_agent_pipeline

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
