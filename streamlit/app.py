import streamlit as st
import requests
import pandas as pd
import plotly.express as px  # For interactive graphs

# Base URL of your Django backend
BASE_URL = "http://127.0.0.1:8000/"  # Update with your Django server URL

# Inject custom CSS for sidebar styles
st.markdown(
    """
    <style>
    /* Adjust the width of the sidebar */
    [data-testid="stSidebar"] {
        min-width: 200px;
        max-width: 200px;
    }

    /* Adjust sidebar font size and padding */
    [data-testid="stSidebar"] .sidebar-content {
        font-size: 14px;
        padding: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar for Navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Go to:",
    ["Current Cases", "Predictions", "Vaccination Info"]
)

# **1. Current Cases Page**
if page == "Current Cases":
    st.title("Current COVID-19 Cases")

    # Fetch current cases data from Django
    response = requests.get(f"{BASE_URL}current_cases/")
    if response.status_code == 200:
        current_data = response.json().get('current_cases', [])
        if current_data:
            df = pd.DataFrame(current_data)
            st.write("Graph of Current Cases")

            # Plot using Plotly
            fig = px.line(df, x="date", y="cases", title="Current COVID-19 Cases")
            st.plotly_chart(fig)
        else:
            st.write("No data available.")
    else:
        st.error("Failed to fetch current cases.")

# **2. Predictions Page**
elif page == "Predictions":
    st.title("Predicted COVID-19 Cases")

    # Fetch predicted cases data from Django
    response = requests.get(f"{BASE_URL}predict/")
    if response.status_code == 200:
        predictions = response.json().get('predictions', [])

        # Convert predictions into DataFrame
        if predictions:
            prediction_dates = pd.date_range(start="2024-11-01", periods=len(predictions))
            df = pd.DataFrame({"date": prediction_dates, "predicted_cases": predictions})

            st.write("Graph of Predicted Cases")

            # Plot using Plotly
            fig = px.line(df, x="date", y="predicted_cases", title="Predicted COVID-19 Cases")
            st.plotly_chart(fig)
        else:
            st.write("No predictions available.")
    else:
        st.error("Failed to fetch predictions.")

    # Allow user to input a date for prediction
    st.write("Want to see specific predictions?")
    date_input = st.date_input("Select a date to predict cases:")
    if st.button("Get Prediction for Date"):
        if len(predictions) > 0:
            index = (date_input - pd.Timestamp(prediction_dates[0])).days
            if 0 <= index < len(predictions):
                st.write(f"Predicted cases for {date_input}: {predictions[index]}")
            else:
                st.warning("Selected date is out of the 21-day prediction range.")
        else:
            st.warning("Predictions not available.")

# **3. Vaccination Info Page**
elif page == "Vaccination Info":
    st.title("Vaccination Information")

    # Display vaccination info
    st.write("Vaccination is an effective way to combat COVID-19.")
    st.write("To learn more about vaccination programs, visit the Malaysia MoH website:")
    st.markdown("[Visit Malaysia MoH](https://www.moh.gov.my/)")
