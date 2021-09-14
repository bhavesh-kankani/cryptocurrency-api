from rest_framework import serializers
from .models import CoinPrediction

class CoinPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinPrediction
        fields = '__all__'