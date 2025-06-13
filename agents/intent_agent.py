import json
import logging
from typing import TypedDict, Optional

from langchain_core.tools import tool
from langchain.chat_models import AzureChatOpenAI
from prompts.prompt_templates import intent_prompt_template
from core.config import AZURE_DEPLOYMENT_NAME

logger = logging.getLogger(__name__)

llm = AzureChatOpenAI(
    deployment_name=AZURE_DEPLOYMENT_NAME,
    temperature=0.2,
    model_name="gpt-4"
)

class IntentState(TypedDict):
    query: str
    intent: Optional[str]
    confidence: Optional[float]

def intent_recognition_agent(state: IntentState) -> IntentState:
    try:
        response = llm.invoke(intent_prompt_template.format_prompt(query=state["query"]))
        j = json.loads(response.content)
        state["intent"] = j.get("intent", "unknown")
        state["confidence"] = j.get("confidence", 0.0)
        logger.info(f"Intent recognized: {state['intent']} with confidence {state['confidence']}")
        return state
    except Exception as e:
        logger.error(f"Intent recognition failed: {e}")
        state["intent"] = "unknown"
        state["confidence"] = 0.0
        return state
