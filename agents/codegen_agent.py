import json
import logging
from typing import TypedDict, Optional
from langchain.chat_models import AzureChatOpenAI
from prompts.prompt_templates import codegen_prompt_template
from core.config import AZURE_DEPLOYMENT_NAME

logger = logging.getLogger(__name__)

llm = AzureChatOpenAI(
    deployment_name=AZURE_DEPLOYMENT_NAME,
    temperature=0.2,
    model_name="gpt-4"
)

class CodeGenState(TypedDict):
    query: str
    intent: str
    confidence: float
    filtered_metadata: dict
    code: Optional[str]
    language: Optional[str]

def code_generation_agent(state: CodeGenState) -> CodeGenState:
    try:
        prompt_text = codegen_prompt_template.format_prompt(
            intent=state["intent"],
            filtered_metadata=json.dumps(state["filtered_metadata"], indent=2),
            query=state["query"],
            language="pyspark"
        )
        response = llm.invoke(prompt_text)
        code = response.content.strip()
        state["code"] = code
        state["language"] = "pyspark"
        logger.info("Code generation successful.")
        return state
    except Exception as e:
        logger.error(f"Code generation failed: {e}")
        state["code"] = None
        state["language"] = None
        return state
