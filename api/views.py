from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .utils import predict_hybrid

@api_view(['GET'])
def predict_next_day(request):
    prediction = predict_hybrid()
    return Response({'predicted_cases': prediction})
