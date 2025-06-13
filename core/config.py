import os

AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
EMBEDDING_MODEL = os.getenv("AZURE_EMBEDDING_MODEL")
DATA_PATH = "/mnt/data/delta/"
ROLE = "non_clinical_staff"  # In prod, derive from user session
