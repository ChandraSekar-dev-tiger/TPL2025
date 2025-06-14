from typing import TypedDict, Optional, Any
from agents.llm_client import llm_client
from prompts.prompt_templates import reporting_prompt_template
import logging
import traceback

logger = logging.getLogger(__name__)

class ReportingState(TypedDict):
    query: str
    insight: Optional[str]
    result: Optional[Any]
    report_text: Optional[str]
    error_message: Optional[str]
    error_trace: Optional[str]

def reporting_agent(state: ReportingState) -> ReportingState:
    try:
        if not state.get("insight") and not state.get("result"):
            state["report_text"] = "No insights or results to report"
            state["error_message"] = "No insights or results to report"
            state["error_trace"] = traceback.format_exc()
            return state

        prompt_text = reporting_prompt_template.format_prompt(
            insight=state.get("insight", ""),
            result=state.get("result", ""),
        )
        try:
            #TODO: 
            # report = llm_client.call_llm(prompt_text)
            report = f"Markdown Report: {prompt_text}"
            state["report_text"] = report
            state["error_message"] = None
            state["error_trace"] = None
            logger.info("Report generated")
        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            state["report_text"] = "Failed to generate report."
            state["error_message"] = f"LLM call failed: {str(e)}"
            state["error_trace"] = traceback.format_exc()
    except Exception as e:
        logger.error(f"Reporting failed: {str(e)}")
        state["report_text"] = "Failed to generate report."
        state["error_message"] = f"Reporting failed: {str(e)}"
        state["error_trace"] = traceback.format_exc()
    return state
