import asyncio
import logging

# import pandas as pd
import streamlit as st

from core.logging_config import setup_logging
from test_main import query_agent  # , test_codegen_retries

# from enum import Enum


st.set_page_config(layout="wide")

st.title("Healthcare streamlit application")

# Set up logging
setup_logging(log_level="INFO")

logger = logging.getLogger(__name__)

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# Query input
options = ["non_clinical_staff", "administrative_staff", "managers"]
user_role = st.selectbox("Select the role: ", options)
user_query = st.text_input("Enter your query:", "Number of patients in emergency ward")

if st.button("Run Query"):
    if user_query and user_role:
        try:
            with st.spinner("Processing your query..."):
                # Run the query
                result = asyncio.run(
                    query_agent(
                        {
                            "query": user_query,
                            "user_role": user_role,
                            "session_id": st.session_state.session_id,
                        }
                    )
                )

                message_placeholder = st.empty()
                message_placeholder.info("Running backend tests... Please wait.")

                # Update session ID
                st.session_state.session_id = (
                    st.session_state.session_id
                )  # result["session_id"]

                # Display results
                st.success("Analysis complete!")
                message_placeholder.success("Tests completed!")
                st.subheader("Test Results:")
                st.code(result["result"]["code"])  # Display the returned result
                st.write(result["result"]["report"])

        except Exception as e:
            logger.error("Error processing query: %s", str(e))
            st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a query.")
