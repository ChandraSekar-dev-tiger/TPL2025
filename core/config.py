import os
import json

AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME", "your_deployment_name")
EMBEDDING_MODEL = os.getenv("AZURE_EMBEDDING_MODEL", "your_embedding_model")
DATA_PATH = "/mnt/data/delta/"
DEFAULT_ROLE = "non_clinical_staff"

def load_metadata(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)
