from django.shortcuts import render

from django.http import JsonResponse
from api.models import CovidData
from api.utils import preprocess_data, predict_with_hybrid_model
from api.utils import get_all_predictions_from_db, get_all_current_from_db

def predict_cases_view(request):
    """
    Handle user requests for future predictions.
    """
    # Preprocess the latest data
    scaled_data = preprocess_data(window_size=30)

    # Predict future cases
    predictions = predict_with_hybrid_model(scaled_data)

    # Convert predictions to standard Python floats for JSON serialization
    predictions = [float(prediction) for prediction in predictions]

    # Return predictions as JSON
    return JsonResponse({'predictions': predictions})

def current_cases_view(request):
    """
    Fetch and return the latest COVID-19 cases.
    """
    current_cases = list(CovidData.objects.order_by('-date').values('date', 'cases')[:1])
    return JsonResponse({'current_cases': current_cases})


def show_all_predictions(request):
    predictions = get_all_predictions_from_db()
    return JsonResponse({'predictions': predictions})


def show_all_current_cases(request):
    current_cases = get_all_current_from_db()
    return JsonResponse({'current_cases': current_cases})
