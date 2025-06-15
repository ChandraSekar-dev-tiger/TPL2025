import requests
import streamlit as st
from streamlit_tags import st_tags

st.title("Healthcare Metric Assistant")
st.write("Enter your question below to get insights about healthcare metrics:")

# Text input for the user's question
# user_query = st.text_input("Your Question:")
user_query = st_tags(
    label="",
    text="Enter your query:",
    value="",
    suggestions=[
        "How many patients visited?",
        "Average wait time in ER",
        "Monthly financial overview",
    ],
    maxtags=1,
    key="1",
)

# Button to get insights
if st.button("Get Insights") and user_query:
    with st.spinner("Analyzing..."):
        try:
            # Send the query to your AI backend
            api_endpoint = (
                "http://localhost:8000/api/query"  # Replace with your API URL
            )
            response = requests.post(api_endpoint, json={"query": user_query})

            if response.status_code == 200:
                data = response.json()
                # Display response as per template
                st.markdown(
                    f"**Based on your query about '{user_query}', I've identified the following relevant KPIs:**"
                )
                st.write(f"**Primary KPI:** {data.get('KPI')}")
                st.write(f"**Source Table:** {data.get('Table')}")
                st.write(f"**Related Metrics:** {data.get('Related')}")
                st.write(f"**Analysis Scope:** {data.get('Scope')}")

                st.markdown("### Generated Code for Your Analysis")
                st.code(data.get("CodeSnippet"), language="python")

                st.markdown("### Insights")
                st.write(data.get("Insight"))
            else:
                st.error("Failed to retrieve insights. Please try again.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
