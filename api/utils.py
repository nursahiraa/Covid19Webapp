import requests
import pandas as pd
from io import StringIO
from .models import CovidData
import tensorflow as tf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import joblib
from keras.models import load_model


# Load the Random Forest model
with open('api/models/Random_Forest.pkl', 'rb') as f:
    rf_model = joblib.load(f)

# Load LSTM model
lstm_model = load_model('api/models/LSTM.keras', compile=False)
lstm_model.compile(optimizer='adam', loss='mean_squared_error')

# Initialize scaler (ensure it's consistent with your training scaler)
scaler = MinMaxScaler(feature_range=(0, 1))

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



def preprocess_data(window_size=30):
    """
    Fetches recent data from the database, scales it, and prepares it for the hybrid model.
    :param window_size: Number of days to consider for sliding windows.
    :return: Preprocessed input for Random Forest and LSTM.
    """
    # Fetch the latest cases from the database
    data = list(CovidData.objects.order_by('-date').values_list('cases', flat=True))[:window_size]
    data.reverse()  # Ensure chronological order

    # Scale the data using the same scaler as during training
    scaled_data = scaler.fit_transform(np.array(data).reshape(-1, 1))

    return scaled_data



def predict_hybrid(window_size=30):
    """
    Predict the next day's cases using the hybrid (RF + LSTM) model.
    :param window_size: Number of days to consider for the sliding window.
    :return: Predicted cases for the next day (rescaled to original scale).
    """
    # Preprocess data
    scaled_data = preprocess_data(window_size)

    # Step 1: Predict with Random Forest
    rf_input = scaled_data[-window_size:].flatten().reshape(1, -1)  # Flatten for RF input
    rf_prediction = rf_model.predict(rf_input)[0]

    # Step 2: Prepare LSTM input (cases_new + RF prediction)
    lstm_input = np.concatenate((scaled_data[-window_size:], [[rf_prediction]]), axis=1)  # Add RF prediction
    lstm_input = lstm_input.reshape(1, -1, 2)  # Shape: (1, timesteps, features)

    # Step 3: Predict with LSTM
    lstm_prediction = lstm_model.predict(lstm_input)[0][0]

    # Step 4: Rescale LSTM prediction back to original scale
    lstm_prediction_rescaled = scaler.inverse_transform([[lstm_prediction]])[0][0]

    return int(lstm_prediction_rescaled)











# def predict_cases(input_data):
#     """
#     Predict the next day's cases using the hybrid model.
#
#     :param input_data: A list of case numbers (e.g., last 30 days of cases)
#     :return: Predicted cases for the next day
#     """
#     # Ensure input_data is in the correct format for the model
#     input_data = np.array(input_data).reshape(1, -1, 1)  # Example: (batch_size=1, timesteps=30, features=1)
#
#     # Make a prediction
#     prediction = model.predict(input_data)
#
#     # Return the predicted value (rounded for convenience)
#     return int(prediction[0][0])
#
#
# def make_prediction():
#     recent_data = get_recent_data()
#     prediction = predict_cases(recent_data)
#     print(f"Predicted cases for tomorrow: {prediction}")
#     return prediction