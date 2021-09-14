from django.urls import path
from .views import home, predict

urlpatterns = [
    path('', home),
    path('predictions/<coin>/', predict)
]