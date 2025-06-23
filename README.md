# Project Title

Brief description of your project.

## Project Structure

```
.
├── README.md
├── agents                          ## folder containing all the agent scripts
│   ├── __init__.py
│   ├── codegen_agent.py
│   ├── execution_agent.py
│   ├── intent_agent.py
│   ├── interpretation_agent.py
│   ├── llm_client.py
│   ├── logical_check_agent.py
│   ├── reporting_agent.py
│   └── retrieval_agent.py
├── core                            ## Core components for the pipeline
│   ├── __init__.py
│   ├── config.py
│   ├── execute_code_tool.py
│   ├── logging_config.py
│   ├── metadata_filter.py
│   └── session_manager.py
├── guardrail.py                   ## guardrail script to track violation
├── main.py                        ## main script to test the entire code
├── main_backup.py
├── metadata
│   ├── HospitalinfoPatientsClinicaldata.xlsx
│   ├── NonClinicalMetricsschema.xlsx
│   └── NonClinical_sheets_data.json
├── notebooks                      ## Notebooks used for testing
│   ├── create_metadata_file.ipynb
│   ├── full_role_based_metric_access.json
│   ├── non_clinical_metrics_access.csv
│   ├── non_clinical_metrics_metadata.json
│   └── read_rag.ipynb
├── pipelines                      ## Pipelines schema
│   ├── __init__.py
│   └── pipeline.py
├── prompts                        ## all prompts used by the respective agents
│   ├── __init__.py
│   └── prompt_templates.py
├── pyproject.toml
├── streamlitapp.py                ## Streamlit application code
├── test.ipynb
├── test_main.py
└── uv.lock                        ## uv lock to sync the env in your local
```

## Environment Setup

This project uses [uv](https://github.com/astral-sh/uv) for fast Python environment management and reproducible installs.

### Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) installed
  Install via pipx or pip:
  ```bash
  pip install uv
  ```

### Installing Dependencies

To create a virtual environment and install all dependencies as locked in `uv.lock`:

```bash
uv sync
```
Note: Make sure you are not using any python or conda env while perfomring the above steps

## Usage

Activate the environment:

```bash
source .venv/bin/activate
```

## Running the main scripts for test

```bash
uv run test_app.py
```

## Running the streamlit app

```bash
streamlit run streamlitapp.py
```