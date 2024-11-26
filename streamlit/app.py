import streamlit as st
import requests

# Base URL of your Django backend
BASE_URL = "http://127.0.0.1:8000/"

st.title("COVID-19 Case Prediction Dashboard")

# Tabs for navigation
tab1, tab2 = st.tabs(["Future Predictions", "Current Cases"])

# **Tab 1: Future Predictions**
with tab1:
    st.header("Predict COVID-19 Cases for a Future Date")
    # Input for selecting a date
    date_input = st.date_input("Select a date to predict cases:")

    if st.button("Get Prediction"):
        # Fetch predictions from Django
        response = requests.get(f"{BASE_URL}predict/")
        if response.status_code == 200:
            predictions = response.json().get('predictions', [])
            st.write(f"Predicted cases for {date_input}: {predictions}")
        else:
            st.error("Failed to fetch predictions from the backend.")

# **Tab 2: Current Cases**
with tab2:
    st.header("Current COVID-19 Cases")
    if st.button("Get Current Cases"):
        # Fetch current cases from Django
        response = requests.get(f"{BASE_URL}current_cases/")
        if response.status_code == 200:
            current_data = response.json().get('current_cases', [])
            st.write("Latest Current Cases:", current_data)
        else:
            st.error("Failed to fetch current cases.")
