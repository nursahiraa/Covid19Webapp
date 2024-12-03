from django.shortcuts import render

from django.http import JsonResponse
from api.models import CovidData
from api.utils import preprocess_data, predict_with_hybrid_model
from api.utils import get_all_predictions_from_db, get_all_current_from_db


def show_all_predictions(request):
    predictions = get_all_predictions_from_db()
    return JsonResponse({'predictions': predictions})


def show_all_current_cases(request):
    current_cases = get_all_current_from_db()
    return JsonResponse({'current_cases': current_cases})
