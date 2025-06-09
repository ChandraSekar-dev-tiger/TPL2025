from enum import Enum

import pandas as pd
import streamlit as st


# Define roles
class Role(Enum):
    DOCTOR = "Doctor"
    NURSE = "Nurse"
    ADMIN = "Admin"


# Mock user database
users_db = {
    "doctor": {"password": "pass@123#", "role": Role.DOCTOR},
    "nurse": {"password": "pass@456#", "role": Role.NURSE},
    "admin": {"password": "admin@789#", "role": Role.ADMIN},
}


# PHI data sample
patients_list = [
    {
        "Name": "Patient1",
        "SSN": "123-45-6789",
        "Medical Record": "MRN1001",
        "Notes": "Patient has a history of headache.",
    },
    {
        "Name": "Patient2",
        "SSN": "234-56-7891",
        "Medical Record": "MRN1002",
        "Notes": "Patient has a history of cold.",
    },
]


# Login Section
def login():
    st.title("Hospital Staff Chatbot Interface")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = users_db.get(username)
        if user and user["password"] == password:
            st.session_state["user"] = {"username": username, "role": user["role"]}
            st.success(f"Welcome, {username} ({user['role'].value})")
        else:
            st.error("Invalid credentials")


# Data masking function
def get_masked_data(role):
    role = Role(role)
    data_lst = []
    for patient_data in patients_list:
        if role == Role.ADMIN:
            data_lst.append(patient_data)
        else:
            masked_data = {}
            for key, value in patient_data.items():
                # if role == Role.ADMIN:
                #     pass
                if role == Role.DOCTOR and key in ["SSN"]:
                    masked_data[key] = "***MASKED***"
                elif role == Role.NURSE and key in ["SSN", "Medical Record"]:
                    masked_data[key] = "***MASKED***"
                else:
                    masked_data[key] = value
            data_lst.append(masked_data)
    return data_lst


def display_patient_data(data):
    df = pd.DataFrame(data)
    st.table(df)


# Chatbot Interface
def chatbot_interface():
    st.header("Patient Data and Chatbot")
    role = st.session_state["user"]["role"].value

    # Show masked or full data based on role
    data_to_display = get_masked_data(role)
    st.subheader("Patient Data")
    # for key, value in data_to_display.items():
    #     st.write(f"**{key}:** {value}")
    display_patient_data(data_to_display)

    # Chat interface
    st.subheader("AI Chatbot")
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            st.markdown(f"**User:** {msg['content']}")
        else:
            st.markdown(f"**Bot:** {msg['content']}")

    user_input = st.text_input("Your message:", key="user_input")
    if st.button("Send"):
        # Placeholder for chatbot response logic
        response = f"Echo: {user_input}"
        st.session_state["messages"].append({"role": "user", "content": user_input})
        st.session_state["messages"].append({"role": "bot", "content": response})


# Main App Logic
def main():
    if "user" not in st.session_state:
        login()
    else:
        # Show main interface with role-based access
        chatbot_interface()
        if st.button("Logout"):
            del st.session_state["user"]
            st.rerun()


if __name__ == "__main__":
    main()
