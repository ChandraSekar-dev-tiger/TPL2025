from typing import TypedDict, Optional, Any
from agents.llm_client import llm_client
from prompts.prompt_templates import interpretation_prompt_template
import logging
import traceback
import pandas as pd
import json

logger = logging.getLogger("agents.interpretation_agent")

class InterpretationState(TypedDict):
    query: str
    intent: Optional[str]
    confidence: Optional[float]
    code: Optional[str]
    language: Optional[str]
    result: Optional[Any]
    insight: Optional[str]
    error_message: Optional[str]
    error_trace: Optional[str]
    current_node: Optional[str]

def interpretation_agent(state: InterpretationState) -> InterpretationState:
    logger.info("Starting interpretation agent")
    logger.debug("Current state: %s", json.dumps(state, default=str))
    
    try:
        # Set current node
        state["current_node"] = "interpretation"
        
        # Check if result exists and is not empty
        result = state.get("result")
        if result is None:
            logger.warning("No results to interpret")
            state["insight"] = "No results to interpret"
            state["error_message"] = "No results to interpret"
            state["error_trace"] = traceback.format_exc()
            return state
            
        # Handle DataFrame results
        if isinstance(result, pd.DataFrame):
            if result.empty:
                logger.warning("Empty DataFrame received")
                state["insight"] = "No data available for interpretation"
                state["error_message"] = "Empty DataFrame received"
                state["error_trace"] = traceback.format_exc()
                return state
            # Convert DataFrame to dict for logging
            result_dict = result.to_dict(orient='records')
            logger.debug("DataFrame result: %s", json.dumps(result_dict, default=str))
        else:
            logger.debug("Result: %s", str(result))

        prompt_text = interpretation_prompt_template.format_prompt(
            intent=state.get("intent", ""),
            result=result,
        )
        logger.debug("Generated prompt: %s", prompt_text)
        
        try:
            # TODO:
            # insight = llm_client.call_llm(prompt_text)
            insight = "beautifull data ;-)"
            state["insight"] = insight
            state["error_message"] = None
            state["error_trace"] = None
            logger.info("Interpretation generated successfully")
        except Exception as e:
            logger.error("LLM call failed: %s", str(e), exc_info=True)
            state["insight"] = None
            state["error_message"] = f"LLM call failed: {str(e)}"
            state["error_trace"] = traceback.format_exc()
    except Exception as e:
        logger.error("Interpretation failed: %s", str(e), exc_info=True)
        state["insight"] = None
        state["error_message"] = f"Interpretation failed: {str(e)}"
        state["error_trace"] = traceback.format_exc()
    
    logger.info("Interpretation agent completed. State updated with %s", 
                "error" if state.get("error_message") else "success")
    return state
