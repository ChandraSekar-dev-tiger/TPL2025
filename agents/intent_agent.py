from typing import TypedDict, Optional
from agents.llm_client import llm_client
import logging
import traceback
import json
from prompts.prompt_templates import intent_prompt_template

logger = logging.getLogger("agents.intent_agent")

class IntentState(TypedDict):
    query: str
    relevance: Optional[int]
    reasoning: Optional[str]
    error_message: Optional[str]
    error_trace: Optional[str]
    current_node: Optional[str]

def intent_recognition_agent(state: IntentState) -> IntentState:
    logger.info("Starting intent recognition with query: %s", state.get("query", "No query provided"))
    logger.debug("Current state: %s", json.dumps(state, default=str))
    
    try:
        # Set current node
        state["current_node"] = "intent_recognition"
        
        prompt_text = intent_prompt_template.format_prompt(query=state["query"])
        try:
            #TODO: change dummy llm return
            j = {
                "relevance": 1,
                "reasoning": "Query is related to healthcare metrics"
            }
            
            # llm_response = llm_client.call_llm(prompt_text)
            # j = json.loads(llm_response)
            state["relevance"] = j.get("relevance", 0)
            state["reasoning"] = j.get("reasoning", "")
            logger.info("Query relevance: %s", state["relevance"])
        except json.JSONDecodeError as e:
            logger.error("Failed to parse LLM response: %s", str(e))
            state["relevance"] = 0
            state["reasoning"] = "Failed to parse response"
            state["error_message"] = f"Failed to parse LLM response: {str(e)}"
            state["error_trace"] = traceback.format_exc()
        except Exception as e:
            logger.error("LLM call failed: %s", str(e))
            state["relevance"] = 0
            state["reasoning"] = "LLM call failed"
            state["error_message"] = f"LLM call failed: {str(e)}"
            state["error_trace"] = traceback.format_exc()
    except Exception as e:
        logger.error("Intent recognition failed: %s", str(e), exc_info=True)
        state["relevance"] = 0
        state["reasoning"] = "Intent recognition failed"
        state["error_message"] = f"Intent recognition failed: {str(e)}"
        state["error_trace"] = traceback.format_exc()
    
    logger.info("Intent recognition completed. State updated with %s", 
                "error" if state.get("error_message") else "success")
    return state
