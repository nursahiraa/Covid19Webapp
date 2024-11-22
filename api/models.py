# Create your database models here.
from django.db import models

class CovidData(models.Model):
    date = models.DateField(unique=True)
    cases = models.IntegerField()

class PredictedCases(models.Model):
    date = models.DateField(unique=True)
    predicted_cases = models.IntegerField()

    def __str__(self):
        return f"{self.date}: {self.predicted_cases}"
