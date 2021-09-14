from django.db import models

# Create your models here.

class CoinPrediction(models.Model):
    coin_name = models.CharField(max_length=10)
    first_day = models.DecimalField(max_digits=20, decimal_places=10)
    second_day = models.DecimalField(max_digits=20, decimal_places=10)
    third_day = models.DecimalField(max_digits=20, decimal_places=10)
    fourth_day = models.DecimalField(max_digits=20, decimal_places=10)
    fifth_day = models.DecimalField(max_digits=20, decimal_places=10)
    sixth_day = models.DecimalField(max_digits=20, decimal_places=10)
    seventh_day = models.DecimalField(max_digits=20, decimal_places=10)
    last_updated = models.DateField(auto_now=True)
