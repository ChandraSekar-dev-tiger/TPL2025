from langchain.prompts import ChatPromptTemplate, PromptTemplate

intent_prompt_template = ChatPromptTemplate.from_template(
    """
You are an intent classifier for healthcare queries.
Determine if the query is relevant to healthcare based on these KPIs:
- Patient outcomes and quality metrics
- Clinical performance indicators
- Healthcare utilization rates
- Cost and financial metrics
- Patient satisfaction scores
- Operational efficiency metrics
- Population health indicators
- Healthcare access metrics

User query:
{query}

Return JSON with these keys:
- 'relevance': 1 if the query is healthcare-related, 0 if not
- 'reasoning': A brief explanation of why the query is or isn't healthcare-relevant
"""
)

codegen_prompt_template = ChatPromptTemplate.from_template(
    """
You are a healthcare data code generation agent.
Using the intent '{intent}' and filtered metadata:
{filtered_metadata}

syntax_errors: {syntax_errors}
logical_errors: {logical_errors}

Generate {language} code that answers the user query:
{query}

Return only the code block without explanation.
"""
)

interpretation_prompt_template = ChatPromptTemplate.from_template(
    """
You are an AI assistant that analyzes the result of a healthcare data query with intent '{intent}'.
Provide a concise, actionable insight in natural language based on this result:

{result}
"""
)

reporting_prompt_template = ChatPromptTemplate.from_template(
    """
You are a reporting assistant. Create a brief, clear report based on the following:
- Insight: {insight}
- Query Result: {result}

Format the report in plain English, starting with the insight, followed by key data points.
"""
)

logical_check_prompt_template = PromptTemplate(
    input_variables=["query", "code", "language"],
    template="""You are a code analysis expert. Analyze the following code for logical issues and potential problems.

Query: {query}
Language: {language}

Code to analyze:
{code}

Please check for the following types of issues:
1. Logical errors in the implementation
2. Edge cases that might cause problems
3. Potential performance issues
4. Data type mismatches
5. Missing error handling
6. Incorrect assumptions about the data

Return a JSON array of issues found, or an empty array if no issues are found. Each issue should include:
- type: The type of issue (logical, edge case, performance, etc.)
- description: A clear description of the issue
- severity: The severity level (high, medium, low)
- suggestion: How to fix the issue

Example response format:
[
    {{
        "type": "logical",
        "description": "The code assumes data is sorted but doesn't verify this",
        "severity": "high",
        "suggestion": "Add a check to verify data is sorted or sort it explicitly"
    }}
]

If no issues are found, return an empty array: []
"""
)
