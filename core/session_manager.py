import uuid
from typing import Optional, Dict

# Simple in-memory session store
# In prod, replace with Redis or DB-backed store with TTL support
_session_store: Dict[str, dict] = {}

def create_session_id() -> str:
    return str(uuid.uuid4())

def get_session_state(session_id: str) -> Optional[dict]:
    return _session_store.get(session_id)

def save_session_state(session_id: str, state: dict) -> None:
    _session_store[session_id] = state

def clear_session(session_id: str) -> None:
    _session_store.pop(session_id, None)
