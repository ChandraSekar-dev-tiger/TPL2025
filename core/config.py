# core/config.py

import os
from dotenv import load_dotenv

load_dotenv()  # Loads from .env

# Azure Model Foundry configs
AZURE_MODEL_FOUNDRY_ENDPOINT = os.getenv("AZURE_MODEL_FOUNDRY_ENDPOINT")
AZURE_MODEL_FOUNDRY_API_KEY = os.getenv("AZURE_MODEL_FOUNDRY_API_KEY")

# Existing configs
AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
EMBEDDING_MODEL = os.getenv("AZURE_EMBEDDING_MODEL")
DATA_PATH = "/mnt/data/delta/"
ROLE = "non_clinical_staff"
