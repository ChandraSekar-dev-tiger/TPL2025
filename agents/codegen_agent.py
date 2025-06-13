from typing import TypedDict, Optional
from agents.llm_client import llm_client
from prompts.prompt_templates import codegen_prompt_template
import json
import logging

logger = logging.getLogger(__name__)

class CodegenState(TypedDict):
    query: str
    intent: str
    confidence: float
    filtered_metadata: dict
    code: Optional[str]
    language: Optional[str]

def code_generation_agent(state: CodegenState) -> CodegenState:
    prompt_text = codegen_prompt_template.format_prompt(
        query=state["query"], 
        metadata=state["filtered_metadata"]
    )
    try:
        response = llm_client.call_llm(prompt_text)
        # Assuming response is JSON with code and language fields
        j = json.loads(response)
        state["code"] = j.get("code", "")
        state["language"] = j.get("language", "python")
        logger.info(f"Generated code in {state['language']}")
    except Exception as e:
        logger.error(f"Code generation failed: {e}")
        state["code"] = ""
        state["language"] = None
    return state
