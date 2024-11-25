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

def predict_cases_for_existing_dates():
    """
    Predict cases for all existing dates in the dataset without changing any other code.
    This method will fetch the historical data, make predictions for each date,
    and return the predictions in a dictionary with dates as keys and predicted cases as values.
    """
    # Fetch all historical data
    historical_data = list(CovidData.objects.order_by('date').values('date', 'cases'))

    # Extract dates and cases
    dates = [entry['date'] for entry in historical_data]

    # Use preprocess_data() to fetch and scale the data
    scaled_cases = preprocess_data(window_size=len(historical_data))

    predictions = {}  # Dictionary to store predictions with corresponding dates

    # Predict for each date starting from the 30th record
    for i in range(30, len(scaled_cases)):
        # Prepare input for Random Forest
        rf_input = scaled_cases[i-30:i].reshape(1, -1)

        # Predict with Random Forest
        rf_prediction = rf_model.predict(rf_input)

        # Prepare input for LSTM
        lstm_input = np.hstack([scaled_cases[i-30:i].reshape(30, 1), np.full((30, 1), rf_prediction[0])])
        lstm_input = lstm_input.reshape(1, 30, 2)

        # Predict with LSTM
        lstm_prediction = lstm_model.predict(lstm_input)

        # Inverse transform the prediction to original scale
        prediction_df = pd.DataFrame(lstm_prediction, columns=["cases_new"])
        predicted_case = scaler.inverse_transform(prediction_df).flatten()[0]

        # Clip negative values
        predicted_case = max(predicted_case, 0)

        # Store the prediction in the dictionary
        predictions[dates[i]] = predicted_case

    return predictions



def predict_with_hybrid_model(data, days=21):
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

        # Clip negative values
        future_cases = max(future_cases, 0)

        # Append the prediction
        predictions.append(future_cases)

        new_case_df = pd.DataFrame([[future_cases]], columns=["cases_new"])  # Wrap in DataFrame
        new_case_scaled = scaler.transform(new_case_df)
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

from sklearn.metrics import mean_squared_error


def calculate_scaled_rmse_for_existing_dates():
    """
    Calculate RMSE in the scaled space for predicted cases against actual cases for existing dates in the dataset.
    This matches the error computation during training.
    :return: Scaled RMSE value
    """
    # Get predicted values
    predictions = predict_cases_for_existing_dates()

    # Fetch actual values for the same dates
    actual_cases = list(CovidData.objects.filter(date__in=predictions.keys()).values_list('cases', flat=True))
    predicted_cases = list(predictions.values())

    # Transform actual and predicted values to the scaled space
    scaled_actual = scaler.transform(pd.DataFrame(actual_cases, columns=["cases_new"]))
    scaled_predicted = scaler.transform(pd.DataFrame(predicted_cases, columns=["cases_new"]))

    # Compute RMSE in the scaled space
    scaled_rmse = np.sqrt(mean_squared_error(scaled_actual, scaled_predicted))

    print(f"Scaled RMSE: {scaled_rmse:.6f}")
    return scaled_rmse

def evaluate_rmse_on_train_test_split():
    """
    Evaluate scaled RMSE separately for:
    - Training set (70% of original data).
    - Test set (30% of original data).
    """
    total_rows = 1716  # Total rows in the dataset during training
    train_rows = int(0.7 * total_rows)  # 70% training set
    test_rows = total_rows - train_rows  # 30% test set

    # Training set evaluation
    train_scaled_cases = preprocess_data(window_size=train_rows)
    scaled_actual_train = train_scaled_cases[30:]
    rf_predictions_train = []
    lstm_predictions_train = []

    for i in range(30, len(train_scaled_cases)):
        rf_input = train_scaled_cases[i-30:i].reshape(1, -1)
        rf_predictions_train.append(rf_model.predict(rf_input)[0])

        lstm_input = np.hstack([
            train_scaled_cases[i-30:i].reshape(30, 1),
            np.full((30, 1), rf_predictions_train[-1])
        ]).reshape(1, 30, 2)

        lstm_predictions_train.append(lstm_model.predict(lstm_input)[0][0])

    scaled_rmse_train = np.sqrt(mean_squared_error(scaled_actual_train, lstm_predictions_train))
    print(f"Scaled RMSE on Training Set: {scaled_rmse_train:.6f}")

    # Test set evaluation
    test_scaled_cases = preprocess_data(window_size=test_rows)
    scaled_actual_test = test_scaled_cases[30:]
    rf_predictions_test = []
    lstm_predictions_test = []

    for i in range(30, len(test_scaled_cases)):
        rf_input = test_scaled_cases[i-30:i].reshape(1, -1)
        rf_predictions_test.append(rf_model.predict(rf_input)[0])

        lstm_input = np.hstack([
            test_scaled_cases[i-30:i].reshape(30, 1),
            np.full((30, 1), rf_predictions_test[-1])
        ]).reshape(1, 30, 2)

        lstm_predictions_test.append(lstm_model.predict(lstm_input)[0][0])

    scaled_rmse_test = np.sqrt(mean_squared_error(scaled_actual_test, lstm_predictions_test))
    print(f"Scaled RMSE on Test Set: {scaled_rmse_test:.6f}")

    return scaled_rmse_train, scaled_rmse_test


