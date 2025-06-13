from typing import TypedDict, Optional
from agents.llm_client import llm_client
from prompts.prompt_templates import interpretation_prompt_template
import logging

logger = logging.getLogger(__name__)

class InterpretationState(TypedDict):
    query: str
    intent: str
    confidence: float
    code: str
    language: str
    result: Optional[str]
    insight: Optional[str]

def interpretation_agent(state: InterpretationState) -> InterpretationState:
    prompt_text = interpretation_prompt_template.format_prompt(
        code=state["code"],
        result=state["result"],
        query=state["query"]
    )
    try:
        insight = llm_client.call_llm(prompt_text)
        state["insight"] = insight
        logger.info("Interpretation generated")
    except Exception as e:
        logger.error(f"Interpretation failed: {e}")
        state["insight"] = None
    return state
