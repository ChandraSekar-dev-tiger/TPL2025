import json
from pipelines.pipeline import run_agent_pipeline
from core.config import ROLE

if __name__ == "__main__":
    # Load metadata JSON here
    with open("./metadata_with_roles.json") as f:
        metadata = json.load(f)

    query = "What is the patient readmission rate for cardiology in the last quarter?"
    output = run_agent_pipeline(query, ROLE, metadata)

    print("\n=== Final Report ===")
    print(output.get("report_text", "No report generated."))
