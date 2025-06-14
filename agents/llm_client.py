import logging

from langchain_openai import AzureChatOpenAI

from core.config import AZURE_MODEL_FOUNDRY_ENDPOINT, AZURE_MODEL_FOUNDRY_API_KEY, AZURE_DEPLOYMENT_NAME, AZURE_API_VERSION

logger = logging.getLogger(__name__)

class AzureModelFoundryClient:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            api_version=AZURE_API_VERSION,
            azure_endpoint=AZURE_MODEL_FOUNDRY_ENDPOINT,
            azure_deployment=AZURE_DEPLOYMENT_NAME,
            api_key=AZURE_MODEL_FOUNDRY_API_KEY,
        )

    def call_llm(self, prompt: str) -> str:
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"Error calling Azure Model Foundry LLM: {e}")
            raise e


# Create singleton client to be reused by agents
llm_client = AzureModelFoundryClient()
