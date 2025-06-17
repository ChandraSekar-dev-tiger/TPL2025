import logging
import traceback
import json

from typing import TypedDict, Optional
from openai import AzureOpenAI

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.models import VectorizedQuery
from azure.search.documents import SearchClient, IndexDocumentsBatch

from core.config import (AOAI_ENDPOINT, AOAI_KEY, AOAI_API_VERSION,
                         AOAI_EMBEDDING_MODEL_DEPLOYMENT,
                         SEARCH_ENDPOINT, SEARCH_KEY, INDEX_NAME)


# Get logger for this module
logger = logging.getLogger("agents.retrieval_agent")

# Initialize Azure OpenAI client
client = AzureOpenAI(
  api_key=AOAI_KEY,
  api_version=AOAI_API_VERSION,
  azure_endpoint=AOAI_ENDPOINT
)


def generate_embedding(text, model=AOAI_EMBEDDING_MODEL_DEPLOYMENT):
    """Generates a vector embedding for a given piece of text."""
    try:
        # OpenAI API does not accept empty strings, so we send a space instead
        return client.embeddings.create(input=[text if text.strip() else " "],
                                        model=model).data[0].embedding
    except Exception as e:
        print(f"Error generating embedding for text: '{text[:50]}...'. Error: {e}")
        return None


class RetrievalState(TypedDict):
    query: str
    user_role: str
    intent: Optional[str]
    confidence: Optional[float]
    filtered_metadata: Optional[dict]
    error_message: Optional[str]
    error_trace: Optional[str]
    current_node: Optional[str]


def retrieval_agent(state: RetrievalState) -> RetrievalState:
    logger.info("Starting retrieval agent with query: %s", state.get("query", "No query provided"))
    logger.debug("Current state: %s", json.dumps(state, default=str))
    
    try:
        # Set current node
        state["current_node"] = "retrieval"
        
        user_query = state.get("query", "No query provided")
        user_role = state.get("user_role", "No role provided")

        # 1. Generate an embedding for the user's query
        query_vector = generate_embedding(user_query)

        # 2. Perform the vector search with a role filter
        if query_vector:
            vector_query = VectorizedQuery(vector=query_vector,
                                           k_nearest_neighbors=3,
                                           fields="content_vector")
            
            search_client = SearchClient(endpoint=SEARCH_ENDPOINT,
                                         index_name=INDEX_NAME,
                                         credential=AzureKeyCredential(SEARCH_KEY))

            # *** FINAL CODE CHANGE ***
            # Using a standard text search (`search_text`) on the `accessible_to_roles`
            # field. This is a more direct and reliable method than using a complex filter.
            results = search_client.search(
                search_text=user_role,
                search_fields=["accessible_to_roles"],
                vector_queries=[vector_query],
                select=["table_name", "column_name", "content", "accessible_to_roles"],
                top=3,  # Adjust the number of results as needed
            )

            # 3. Print the results
            logger.info(f"Query: '{user_query}'")
            logger.info(f"Role: '{user_role}'\n")
            logger.info("Relevant results from our knowledge base for this role:\n")
            
            # Check if the iterator has any items before looping
            results_list = list(results)
            if not results_list:
                logger.info("No results found for the given query and role.")
            else:
                logger.info(f"Found {len(results_list)} results:")
                cleaned_results = [
                    {
                        "KPI/Metric": item["column_name"],
                        "content": item["content"],
                        "table_name": item["table_name"]
                    }
                    for item in results_list
                ]
        else:
            logger.info("Could not generate a query vector.")

        state["filtered_metadata"] = cleaned_results
        logger.info("Successfully filtered metadata with %d items", len(cleaned_results))
        logger.debug("Filtered metadata: %s", json.dumps(cleaned_results, indent=2))
        
    except Exception as e:
        logger.error("Retrieval failed: %s", str(e), exc_info=True)
        state["filtered_metadata"] = {}
        state["error_message"] = f"Retrieval failed: {str(e)}"
        state["error_trace"] = traceback.format_exc()
    
    logger.info("Retrieval agent completed. State updated with %s", 
                "error" if state.get("error_message") else "success")
    return state
