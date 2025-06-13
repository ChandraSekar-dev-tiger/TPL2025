import os
import requests
import logging
from core.config import AZURE_MODEL_FOUNDRY_ENDPOINT, AZURE_MODEL_FOUNDRY_API_KEY

logger = logging.getLogger(__name__)

class AzureModelFoundryClient:
    def __init__(self):
        self.endpoint = AZURE_MODEL_FOUNDRY_ENDPOINT
        self.api_key = AZURE_MODEL_FOUNDRY_API_KEY
        if not self.endpoint or not self.api_key:
            raise ValueError("Azure Model Foundry endpoint and API key must be set in environment variables")

    def call_llm(self, prompt: str) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {
            "prompt": prompt,
            "max_tokens": 1024,
            "temperature": 0.2,
            # Add other Model Foundry params here if needed
        }
        try:
            response = requests.post(self.endpoint, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            # Assuming response JSON shape includes "choices" -> first choice -> "text"
            text = data.get("choices", [{}])[0].get("text", "")
            return text.strip()
        except Exception as e:
            logger.error(f"Error calling Azure Model Foundry LLM: {e}")
            raise e

# Create singleton client to be reused by agents
llm_client = AzureModelFoundryClient()
