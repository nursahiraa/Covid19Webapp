import requests
import pandas as pd
from io import StringIO
from .models import CovidData
import tensorflow as tf
import numpy as np


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


# Load the hybrid model once for efficiency
model = tf.keras.models.load_model('api/models/hybrid_model.keras')


def predict_cases(input_data):
    """
    Predict the next day's cases using the hybrid model.

    :param input_data: A list of case numbers (e.g., last 30 days of cases)
    :return: Predicted cases for the next day
    """
    # Ensure input_data is in the correct format for the model
    input_data = np.array(input_data).reshape(1, -1, 1)  # Example: (batch_size=1, timesteps=30, features=1)

    # Make a prediction
    prediction = model.predict(input_data)

    # Return the predicted value (rounded for convenience)
    return int(prediction[0][0])


def make_prediction():
    recent_data = get_recent_data()
    prediction = predict_cases(recent_data)
    print(f"Predicted cases for tomorrow: {prediction}")
    return prediction