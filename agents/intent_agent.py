from typing import TypedDict
from prompts.prompt_templates import intent_prompt_template
from agents.llm_client import llm_client
import json
import logging

logger = logging.getLogger(__name__)

class IntentState(TypedDict):
    query: str
    intent: str
    confidence: float

def intent_recognition_agent(state: IntentState) -> IntentState:
    prompt_text = intent_prompt_template.format_prompt(query=state["query"])
    try:
        llm_response = llm_client.call_llm(prompt_text)
        j = json.loads(llm_response)
        state["intent"] = j.get("intent", "unknown")
        state["confidence"] = j.get("confidence", 0.0)
        logger.info(f"Intent recognized: {state['intent']} with confidence {state['confidence']}")
    except Exception as e:
        logger.error(f"Intent recognition failed: {e}")
        state["intent"] = "unknown"
        state["confidence"] = 0.0
    return state
