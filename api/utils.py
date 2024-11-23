from datetime import timedelta
import requests
import pandas as pd
from io import StringIO
from .models import CovidData, PredictedCases
import numpy as np
import joblib
from keras.models import load_model
import matplotlib.pyplot as plt


# Load the pre-fitted scaler
with open('api/models/scaler.pkl', 'rb') as s:
    scaler = joblib.load(s)

# Load the Random Forest model
with open('api/models/Random_Forest.pkl', 'rb') as f:
    rf_model = joblib.load(f)

# Load LSTM model
lstm_model = load_model('api/models/LSTM.keras', compile=False)
lstm_model.compile(optimizer='adam', loss='mean_squared_error')


RAW_URL = "https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/refs/heads/main/epidemic/cases_malaysia.csv"

def fetch_and_update_data():
    response = requests.get(RAW_URL)
    if response.status_code == 200:
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)

        for _, row in df.iterrows():
            CovidData.objects.update_or_create(
                date=row['date'],
                defaults={'cases': row['cases_new']}
            )
        print("Data fetched and updated successfully!")
    else:
        print(f"Failed to fetch data: {response.status_code}")



def get_recent_data(window_size=30):
    data = list(CovidData.objects.order_by('-date').values_list('cases', flat=True))[:window_size]
    return data[::-1]  # Reverse to chronological order

# def preprocess_data(window_size=30, max_rows=1716):
def preprocess_data(window_size=30):
    """
    Fetches recent data from the database, scales it using the pre-fitted scaler.
    """
    # Fetch recent data
    data = list(CovidData.objects.order_by('-date').values_list('cases', flat=True))[:window_size]
    data.reverse()  # Ensure chronological order

    # Convert to DataFrame to provide feature names
    data_df = pd.DataFrame(data, columns=["cases_new"])

    # Transform using the pre-fitted scaler
    scaled_data = scaler.transform(data_df)

    return scaled_data



def predict_with_hybrid_model(data, days=365):
    """
    Predict future cases for a specified number of days using the hybrid model.
    :param data: Preprocessed data (scaled and formatted for the models).
    :param days: Number of future days to predict.
    :return: Predicted cases for the next 'days' days.
    """
    predictions = []
    current_data = data.copy()

    for _ in range(days):
        # Ensure data is 2D for Random Forest
        rf_input = current_data.reshape(1, -1)

        # Predict with Random Forest
        rf_predictions = rf_model.predict(rf_input)  # Single prediction

        # Prepare input for LSTM
        lstm_input = np.hstack([current_data[-30:].reshape(30, 1), np.full((30, 1), rf_predictions[0])])
        lstm_input = lstm_input.reshape(1, 30, 2)  # Reshape to 3D for LSTM input

        # Predict with LSTM
        lstm_predictions = lstm_model.predict(lstm_input)

        # Convert scaled output back to the original scale
        # Wrap predictions in a DataFrame with correct column name
        predictions_df = pd.DataFrame(lstm_predictions, columns=["cases_new"])
        future_cases = scaler.inverse_transform(predictions_df).flatten()[0]

        # Convert scaled output back to the original scale
        # future_cases = scaler.inverse_transform(lstm_predictions).flatten()[0]

        # Clip negative values
        future_cases = max(future_cases, 0)

        # Append the prediction
        predictions.append(future_cases)

        new_case_df = pd.DataFrame([[future_cases]], columns=["cases_new"])  # Wrap in DataFrame
        new_case_scaled = scaler.transform(new_case_df)
        # Update current data with the new prediction
        # new_case_scaled = scaler.transform([[future_cases]])
        current_data = np.append(current_data[1:], new_case_scaled)

    return predictions



def save_predictions_to_db(predictions, start_date):
    """
    Save predicted cases to the database.
    :param predictions: List of predicted cases.
    :param start_date: Date from which predictions start.
    """
    for i, predicted_case in enumerate(predictions):
        predicted_date = start_date + timedelta(days=i)
        PredictedCases.objects.update_or_create(
            date=predicted_date,
            defaults={'predicted_cases': int(predicted_case)}
        )
    print("Predicted cases saved to the database successfully!")



def visualize_predictions(predictions):
    """
    Visualizes the predicted cases over time.
    :param predictions: List of predicted case numbers.
    """
    plt.plot(predictions)
    plt.title("Predicted COVID-19 Cases")
    plt.xlabel("Days Ahead")
    plt.ylabel("Cases")
    plt.show()
