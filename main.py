from pipelines.pipeline import run_agent_pipeline

if __name__ == "__main__":
    query = "What is the patient readmission rate for cardiology in the last quarter?"
    result = run_agent_pipeline(query)
    print("\n=== Final Report ===")
    print(result.get("report_text", "No report generated."))
