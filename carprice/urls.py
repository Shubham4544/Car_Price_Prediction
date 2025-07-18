from django.urls import path
from .views import car_input_view

urlpatterns = [
    path('', car_input_view, name='car_input'),
]
