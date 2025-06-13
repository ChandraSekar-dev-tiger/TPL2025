import logging
from typing import TypedDict, Optional

logger = logging.getLogger(__name__)

class ReportingState(TypedDict):
    query: str
    insight: str
    result: any
    report_text: Optional[str]

def reporting_agent(state: ReportingState) -> ReportingState:
    try:
        report = f"Actionable Insight:\n{state['insight']}\n\nRaw Result:\n{str(state['result'])[:1000]}"
        state["report_text"] = report
        logger.info("Reporting complete.")
        return state
    except Exception as e:
        logger.error(f"Reporting failed: {e}")
        state["report_text"] = "Failed to generate report."
        return state
