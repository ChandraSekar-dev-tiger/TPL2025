from langchain.prompts import ChatPromptTemplate

intent_prompt_template = ChatPromptTemplate.from_template(
    """
You are an intent classifier for healthcare queries.
Classify the intent of this user query into one of the categories:
- aggregate_query
- trend_analysis
- comparison
- general_query
- unknown

User query:
{query}

Return only JSON with keys 'intent' and 'confidence' (0-1).
"""
)

retrieval_prompt_template = ChatPromptTemplate.from_template(
    """
You are a retrieval agent.
Based on the intent '{intent}' and role-based metadata, determine the relevant data fields and tables.

Metadata (filtered by role):
{filtered_metadata}

User query:
{query}

Return JSON of relevant metadata keys and descriptions.
"""
)

codegen_prompt_template = ChatPromptTemplate.from_template(
    """
You are a healthcare data code generation agent.
Using the intent '{intent}' and filtered metadata:
{filtered_metadata}

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
