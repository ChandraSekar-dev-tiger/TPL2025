import logging
from typing import TypedDict, Optional
from langchain.chat_models import AzureChatOpenAI
from prompts.prompt_templates import interpretation_prompt_template
from core.config import AZURE_DEPLOYMENT_NAME

logger = logging.getLogger(__name__)

llm = AzureChatOpenAI(
    deployment_name=AZURE_DEPLOYMENT_NAME,
    temperature=0.2,
    model_name="gpt-4"
)

class InterpretationState(TypedDict):
    query: str
    intent: str
    confidence: float
    code: str
    language: str
    result: str
    insight: Optional[str]

def interpretation_agent(state: InterpretationState) -> InterpretationState:
    try:
        prompt_text = interpretation_prompt_template.format_prompt(
            intent=state["intent"],
            result=state["result"]
        )
        response = llm.invoke(prompt_text)
        insight = response.content.strip()
        state["insight"] = insight
        logger.info("Insight generated.")
        return state
    except Exception as e:
        logger.error(f"Interpretation failed: {e}")
        state["insight"] = "Insight generation failed."
        return state
