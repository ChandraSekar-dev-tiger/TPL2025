from typing import TypedDict, Optional

class ReportingState(TypedDict):
    query: str
    insight: str
    result: str
    report_text: Optional[str]

def reporting_agent(state: ReportingState) -> ReportingState:
    try:
        report = f"Actionable Insight:\n{state['insight']}\n\nRaw Result:\n{state['result'][:1000]}"
        state["report_text"] = report
        return state
    except Exception:
        state["report_text"] = "Failed to generate report."
        return state
