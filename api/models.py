# Create your database models here.
from django.db import models

class CovidData(models.Model):
    date = models.DateField(unique=True)
    cases = models.IntegerField()

class Prediction(models.Model):
    date = models.DateField(unique=True)
    predicted_cases = models.IntegerField()

