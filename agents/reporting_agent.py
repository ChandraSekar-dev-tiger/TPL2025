from typing import TypedDict, Optional
from agents.llm_client import llm_client
from prompts.prompt_templates import reporting_prompt_template
import logging

logger = logging.getLogger(__name__)

class ReportingState(TypedDict):
    query: str
    insight: Optional[str]
    result: Optional[str]
    report_text: Optional[str]

def reporting_agent(state: ReportingState) -> ReportingState:
    prompt_text = reporting_prompt_template.format_prompt(
        insight=state.get("insight", ""),
        result=state.get("result", ""),
        # query=state.get("query", "")
    )
    try:
        #TODO: 
        # report = llm_client.call_llm(prompt_text)
        report = "Markdown Report"
        state["report_text"] = report
        logger.info("Report generated")
    except Exception as e:
        logger.error(f"Reporting failed: {e}")
        state["report_text"] = "Failed to generate report."
    return state
