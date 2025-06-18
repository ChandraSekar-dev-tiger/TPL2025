# core/config.py

import os
from dotenv import load_dotenv

load_dotenv()  # Loads from .env

# Azure Model Foundry configs
AZURE_MODEL_FOUNDRY_ENDPOINT = os.getenv("AZURE_MODEL_FOUNDRY_ENDPOINT")
AZURE_MODEL_FOUNDRY_API_KEY = os.getenv("AZURE_MODEL_FOUNDRY_API_KEY")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
EMBEDDING_MODEL = os.getenv("AZURE_EMBEDDING_MODEL")

# Azure Embedding Model
AOAI_ENDPOINT = os.getenv("AOAI_ENDPOINT")
AOAI_KEY = os.getenv("AOAI_KEY")
AOAI_API_VERSION = os.getenv("AOAI_API_VERSION")
AOAI_EMBEDDING_MODEL_DEPLOYMENT = os.getenv("AOAI_EMBEDDING_MODEL_DEPLOYMENT")

# Azure AI Search
SEARCH_ENDPOINT =os.getenv("SEARCH_ENDPOINT")
SEARCH_KEY =os.getenv("SEARCH_KEY")
INDEX_NAME = os.getenv("INDEX_NAME")

# Databricks configs
DATABRICKS_SERVER_HOSTNAME = os.getenv("DATABRICKS_SERVER_HOSTNAME")
DATABRICKS_HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")
DATABRICKS_ACCESS_TOKEN = os.getenv("DATABRICKS_ACCESS_TOKEN")

DATA_PATH = "/mnt/data/delta/"
ROLE = "non_clinical_staff"
