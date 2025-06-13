from typing import TypedDict, Optional
from core.metadata_filter import filter_metadata_by_role
from core.config import DEFAULT_ROLE, load_metadata

class RetrievalState(TypedDict):
    query: str
    intent: str
    confidence: float
    filtered_metadata: Optional[dict]

# Load metadata once
metadata = load_metadata("./data/metadata_with_roles.json")

def retrieval_agent(state: RetrievalState) -> RetrievalState:
    try:
        filtered_metadata = filter_metadata_by_role(metadata, DEFAULT_ROLE)
        state["filtered_metadata"] = filtered_metadata
        return state
    except Exception as e:
        print(f"Retrieval failed: {e}")
        state["filtered_metadata"] = {}
        return state
