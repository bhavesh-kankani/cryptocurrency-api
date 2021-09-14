from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response


import requests
import json
import pandas as pd
import numpy as np
from tensorflow import keras
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, date

from .models import CoinPrediction
from .serializers import CoinPredictionSerializer

coin_symbols = {
    "Bitcoin":"BTC",
    "Ethereum":"ETH",
    "Dogecoin":"DOGE",
    "Ripple":"XRP",
    "Litecoin":"LTC",
    "Stellar":"XLM",
    "Tether":"USDT"
    }


scaler = MinMaxScaler(feature_range = (0, 1))



def home(request):
    return HttpResponse('<h1>Hello world</h1>')


class MLPredictions:
    def __init__(self, coin):
        self.coin = coin
        self.coin_code = coin_symbols[coin]
        self.last_updated = CoinPrediction.objects.get(coin_name = self.coin).last_updated

    def get_test_data(self):
        url = "https://min-api.cryptocompare.com/data/histoday"
        lookback_days = 30
        res = requests.get(url + f"?fsym={self.coin_code}&tsym=USD&limit=40")
        df = pd.DataFrame(json.loads(res.content)['Data'])

        # getting test_data
        res = requests.get(url + f"?fsym={self.coin_code}&tsym=USD&limit=6")
        test_data = pd.DataFrame(json.loads(res.content)['Data'])

        # concatenating the df (dataframe) and test_data
        total_dataset = pd.concat((df['close'], test_data['close']), axis=0)
        total_dataset.index = pd.to_datetime(total_dataset.index)

        model_inputs = total_dataset[len(total_dataset)-len(test_data)-lookback_days:].values
        model_inputs = model_inputs.reshape(-1, 1)
        model_inputs = scaler.fit_transform(model_inputs)

        # preparing test data
        x_test = []
        for x in range(lookback_days, len(model_inputs)):
            x_test.append(model_inputs[x-lookback_days:x, 0])
        x_test = np.array(x_test)
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
        return x_test



    def predict(self, x_test):
        model_1 = keras.models.load_model("./ml_models/model_1")
        predictions = model_1.predict(x_test)
        del model_1
        predictions = scaler.inverse_transform(predictions)
        return [float(x[0]) for x in predictions]


def update_database(predictions, coin):
    pred = CoinPrediction.objects.get(coin_name = coin)
    pred.first_day = predictions[0]
    pred.second_day = predictions[1]
    pred.third_day = predictions[2]
    pred.fourth_day = predictions[3]
    pred.fifth_day = predictions[4]
    pred.sixth_day =  predictions[5]
    pred.seventh_day = predictions[6]
    pred.last_updated = date.today()
    pred.save()

def modify_serializer_data(serializer_data, coin_code):
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", 'Sun']
    day = datetime.today().weekday() + 1
    res = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={coin_code}&tsyms=USD')
    today_price = json.loads(res.content)['USD']
    data = {"Today": today_price}
    for x in serializer_data:
        if x == "id" or x == "coin_name" or x == "last_updated":
            pass
        elif x == 'first_day':
            data["Tmrw"] = float(serializer_data[x])
        else:
            data[days[(day+1)%7]] = float(serializer_data[x])
            day += 1
    return data


@api_view(['GET'])
def predict(request, coin):
    ml_predictions = MLPredictions(coin)
    if (date.today() - ml_predictions.last_updated).days >= 1:
        predictions = ml_predictions.predict(ml_predictions.get_test_data())
        update_database(predictions, coin)
    predictions = CoinPrediction.objects.get(coin_name = coin)

    serializer = CoinPredictionSerializer(predictions)
    data = modify_serializer_data(serializer.data, coin_symbols[coin])
    return Response(data)