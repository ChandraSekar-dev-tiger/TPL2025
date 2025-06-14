from typing import TypedDict, Optional
from agents.llm_client import llm_client
import logging

logger = logging.getLogger(__name__)

class RetrievalState(TypedDict):
    query: str
    intent: str
    confidence: float
    filtered_metadata: Optional[dict]

def retrieval_agent(state: RetrievalState) -> RetrievalState:
    try:
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
        logger.info(f"Metadata filtered: {filtered_metadata}")
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        state["filtered_metadata"] = {}
    return state
