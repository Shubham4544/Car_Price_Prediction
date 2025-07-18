from django.shortcuts import render, redirect
from .forms import CarInputForm
from .models import CarInput
from django.contrib.auth.decorators import login_required
import pickle
import pandas as pd

model = pickle.load(open('model.pkl', 'rb'))

def encode_inputs(car):
    replacements = {
        'owner': {'First Owner': 1, 'Second Owner': 2, 'Third Owner': 3,
                  'Fourth & Above Owner': 4, 'Test Drive Car': 5},
        'fuel': {'Diesel': 1, 'Petrol': 2, 'LPG': 3, 'CNG': 4},
        'seller_type': {'Individual': 1, 'Dealer': 2, 'Trustmark Dealer': 3},
        'transmission': {'Manual': 1, 'Automatic': 2},
        'name': {'Maruti': 1, 'Skoda': 2, 'Honda': 3, 'Hyundai': 4, 'Toyota': 5,
                 'Ford': 6, 'Renault': 7, 'Mahindra': 8, 'Tata': 9, 'Chevrolet': 10,
                 'Datsun': 11, 'Jeep': 12, 'Mercedes-Benz': 13, 'Mitsubishi': 14,
                 'Audi': 15, 'Volkswagen': 16, 'BMW': 17, 'Nissan': 18, 'Lexus': 19,
                 'Jaguar': 20, 'Land': 21, 'MG': 22, 'Volvo': 23, 'Daewoo': 24,
                 'Kia': 25, 'Fiat': 26, 'Force': 27, 'Ambassador': 28, 'Ashok': 29,
                 'Isuzu': 30, 'Opel': 31}
    }

    for field in replacements:
        car[field] = replacements[field].get(car[field], 0)

    return [[car['name'], car['year'], car['km_driven'], car['fuel'],
             car['seller_type'], car['transmission'], car['owner'],
             car['mileage'], car['engine'], car['max_power'], car['seats']]]

@login_required
def car_input_view(request):
    if request.method == 'POST':
        form = CarInputForm(request.POST)
        if form.is_valid():
            car_input = form.save(commit=False)
            car_input.user = request.user
            input_data = encode_inputs(form.cleaned_data)
            car_input.predicted_price = model.predict(input_data)[0]
            car_input.save()
            return render(request, 'carprice/result.html', {'price': car_input.predicted_price})
    else:
        form = CarInputForm()
    return render(request, 'carprice/car_form.html', {'form': form})
from django.shortcuts import render

# Create your views here.
