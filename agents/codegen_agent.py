from typing import TypedDict, Optional
from agents.llm_client import llm_client
from prompts.prompt_templates import codegen_prompt_template
import logging
import traceback
import json

logger = logging.getLogger("agents.codegen_agent")

class CodegenState(TypedDict):
    query: str
    intent: Optional[str]
    confidence: Optional[float]
    filtered_metadata: Optional[dict]
    code: Optional[str]
    language: Optional[str]
    error_message: Optional[str]
    error_trace: Optional[str]
    current_node: Optional[str]
    codegen_attempts: Optional[int]
    max_codegen_attempts: Optional[int]
    previous_errors: Optional[list]

def code_generation_agent(state: CodegenState) -> CodegenState:
    logger.info("Starting code generation agent (attempt %d/%d)", 
                state.get("codegen_attempts", 0) + 1,
                state.get("max_codegen_attempts", 3))
    logger.debug("Current state: %s", json.dumps(state, default=str))
    
    try:
        # Set current node
        state["current_node"] = "code_generation"
        
        # Increment attempt counter
        state["codegen_attempts"] = state.get("codegen_attempts", 0) + 1
        
        # Check if we've exceeded max attempts
        if state["codegen_attempts"] > state.get("max_codegen_attempts", 3):
            logger.error("Maximum code generation attempts reached")
            state["error_message"] = "Maximum code generation attempts reached"
            state["error_trace"] = traceback.format_exc()
            return state
            
        # Generate prompt with previous errors if any
        logger.debug(f"print: {state.get("filtered_metadata", {})}")
        prompt_text = codegen_prompt_template.format_prompt(
            query=state.get("query", ""),
            intent=state.get("intent", ""),
            filtered_metadata=state.get("filtered_metadata", {}),
            language=state.get("language", "python"),
            previous_errors=state.get("previous_errors", [])
        )
        logger.debug("Generated prompt: %s", prompt_text)
        
        try:
            # TODO: Replace with actual LLM call
            # response = llm_client.call_llm(prompt_text)
            # result = json.loads(response)
            
            # Dummy response for testing
            result = {
                "code": "print('Hello, World!')",
                "language": "python"
            }
            
            state["code"] = result.get("code")
            state["language"] = result.get("language")
            state["error_message"] = None
            state["error_trace"] = None
            logger.info("Code generated successfully in %s", state["language"])
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse LLM response: %s", str(e))
            state["code"] = None
            state["language"] = None
            state["error_message"] = f"Failed to parse code generation response: {str(e)}"
            state["error_trace"] = traceback.format_exc()
        except Exception as e:
            logger.error("LLM call failed: %s", str(e))
            state["code"] = None
            state["language"] = None
            state["error_message"] = f"LLM call failed: {str(e)}"
            state["error_trace"] = traceback.format_exc()
            
    except Exception as e:
        logger.error("Code generation failed: %s", str(e), exc_info=True)
        state["code"] = None
        state["language"] = None
        state["error_message"] = f"Code generation failed: {str(e)}"
        state["error_trace"] = traceback.format_exc()
    
    logger.info("Code generation agent completed. State updated with %s", 
                "error" if state.get("error_message") else "success")
    return state
