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
        intent=state["intent"], 
        filtered_metadata=state["filtered_metadata"],
        language=state["language"],
        query=state["query"], 
    )
    try:
        #TODO: change dummy llm return
        j = {"code":"""total_sales_by_category = df.groupby("category")["sales"].sum().reset_index()"""}

        # response = llm_client.call_llm(prompt_text)
        # j = json.loads(response)
        state["code"] = j.get("code", "")
        state["language"] = j.get("language", "python")
        logger.info(f"Generated code in {state['language']}")
    except Exception as e:
        logger.error(f"Code generation failed: {e}")
        state["code"] = ""
        state["language"] = None
    return state
