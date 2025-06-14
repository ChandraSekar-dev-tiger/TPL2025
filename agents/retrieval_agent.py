from typing import TypedDict, Optional
from agents.llm_client import llm_client
import logging
import traceback
import json

# Get logger for this module
logger = logging.getLogger("agents.retrieval_agent")

class RetrievalState(TypedDict):
    query: str
    intent: Optional[str]
    confidence: Optional[float]
    filtered_metadata: Optional[dict]
    error_message: Optional[str]
    error_trace: Optional[str]
    current_node: Optional[str]

def retrieval_agent(state: RetrievalState) -> RetrievalState:
    logger.info("Starting retrieval agent with query: %s", state.get("query", "No query provided"))
    logger.debug("Current state: %s", json.dumps(state, default=str))
    
    try:
        # Set current node
        state["current_node"] = "retrieval"
        
        #TODO: # Replace with actual parsing logic from azure AI search
        filtered_metadata = [{
            "Column Name": "patient_arrival_count_monthly",
            "Data Type": "int64",
            "Description": "Total number of patient arrivals in the month",
            "Granularity": "Monthly",
            "Calculation": "Sum of patient arrivals for the month"
            },
            {
            "Column Name": "patient_arrival_count_daily",
            "Data Type": "object",
            "Description": "Daily count of patient arrivals (JSON format)",
            "Granularity": "Daily (nested)",
            "Calculation": "Aggregated from daily patient logs, may include fractional values due to smoothing or averaging"
            },
            {
            "Column Name": "avg_waiting_time_minutes_monthly",
            "Data Type": "float64",
            "Description": "Average waiting time (arrival to first treatment) in minutes (monthly)",
            "Granularity": "Monthly",
            "Calculation": "Average wait time per month"
            },
        ]

        state["filtered_metadata"] = filtered_metadata
        logger.info("Successfully filtered metadata with %d items", len(filtered_metadata))
        logger.debug("Filtered metadata: %s", json.dumps(filtered_metadata, indent=2))
        
    except Exception as e:
        logger.error("Retrieval failed: %s", str(e), exc_info=True)
        state["filtered_metadata"] = {}
        state["error_message"] = f"Retrieval failed: {str(e)}"
        state["error_trace"] = traceback.format_exc()
    
    logger.info("Retrieval agent completed. State updated with %s", 
                "error" if state.get("error_message") else "success")
    return state
