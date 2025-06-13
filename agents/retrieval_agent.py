import logging
from typing import TypedDict, Optional

from core.metadata_filter import filter_metadata_by_role

logger = logging.getLogger(__name__)

class RetrievalState(TypedDict):
    query: str
    intent: str
    confidence: float
    filtered_metadata: Optional[dict]

def retrieval_agent(state: RetrievalState, metadata: dict, role: str) -> RetrievalState:
    try:
        filtered = filter_metadata_by_role(metadata, role)
        state["filtered_metadata"] = filtered
        return state
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        state["filtered_metadata"] = {}
        return state
