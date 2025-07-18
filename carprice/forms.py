from django import forms
from .models import CarInput
import pandas as pd

cars_data = pd.read_csv('Cardetails.csv')
BRANDS = sorted(cars_data['name'].apply(lambda x: x.split(' ')[0]).unique())
FUEL_CHOICES = sorted(cars_data['fuel'].unique())
SELLER_CHOICES = sorted(cars_data['seller_type'].unique())
TRANSMISSION_CHOICES = sorted(cars_data['transmission'].unique())
OWNER_CHOICES = sorted(cars_data['owner'].unique())

class CarInputForm(forms.ModelForm):
    name = forms.ChoiceField(choices=[(b, b) for b in BRANDS])
    fuel = forms.ChoiceField(choices=[(f, f) for f in FUEL_CHOICES])
    seller_type = forms.ChoiceField(choices=[(s, s) for s in SELLER_CHOICES])
    transmission = forms.ChoiceField(choices=[(t, t) for t in TRANSMISSION_CHOICES])
    owner = forms.ChoiceField(choices=[(o, o) for o in OWNER_CHOICES])

    class Meta:
        model = CarInput
        exclude = ['user', 'predicted_price']
