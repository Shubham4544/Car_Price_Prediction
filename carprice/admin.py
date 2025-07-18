
from django.contrib import admin
from .models import CarInput
from django import forms
import pandas as pd
import pickle

# Load CSV
cars_data = pd.read_csv('Cardetails.csv')
cars_data['name'] = cars_data['name'].apply(lambda x: x.split(' ')[0].strip())

fuel_choices = [(f, f) for f in cars_data['fuel'].dropna().unique()]
seller_choices = [(s, s) for s in cars_data['seller_type'].dropna().unique()]
transmission_choices = [(t, t) for t in cars_data['transmission'].dropna().unique()]
owner_choices = [(o, o) for o in cars_data['owner'].dropna().unique()]
name_choices = [(n, n) for n in sorted(cars_data['name'].dropna().unique())]

# Load Model
model = pickle.load(open('model.pkl', 'rb'))

class CarInputForm(forms.ModelForm):
    class Meta:
        model = CarInput
        exclude = ['user', 'predicted_price']

    name = forms.ChoiceField(choices=name_choices)
    fuel = forms.ChoiceField(choices=fuel_choices)
    seller_type = forms.ChoiceField(choices=seller_choices)
    transmission = forms.ChoiceField(choices=transmission_choices)
    owner = forms.ChoiceField(choices=owner_choices)

# @carprice.register(CarInput)
# class CarInputAdmin(carprice.ModelAdmin):
#     form = CarInputForm
#     list_display = ['name', 'year', 'predicted_price', 'user']
#
#     def save_model(self, request, obj, form, change):
#         obj.user = request.user
#
#         # Prepare model input
#         df = pd.DataFrame([[obj.name, obj.year, obj.km_driven, obj.fuel, obj.seller_type,
#                             obj.transmission, obj.owner, obj.mileage, obj.engine,
#                             obj.max_power, obj.seats]],
#                           columns=['name','year','km_driven','fuel','seller_type',
#                                    'transmission','owner','mileage','engine','max_power','seats'])
#
#         # Encode fields just like the original code
#         mappings = {
#             'owner': {'First Owner': 1, 'Second Owner': 2, 'Third Owner': 3,
#                       'Fourth & Above Owner': 4, 'Test Drive Car': 5},
#             'fuel': {'Diesel': 1, 'Petrol': 2, 'LPG': 3, 'CNG': 4},
#             'seller_type': {'Individual': 1, 'Dealer': 2, 'Trustmark Dealer': 3},
#             'transmission': {'Manual': 1, 'Automatic': 2},
#             'name': {n: i+1 for i, n in enumerate(sorted(cars_data['name'].unique()))}
#         }
#
#         for col, mapping in mappings.items():
#             df[col] = df[col].map(mapping)
#
#         # Predict
#         obj.predicted_price = model.predict(df)[0]
#         super().save_model(request, obj, form, change)

from django.urls import path
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.html import format_html

@admin.register(CarInput)
class CarInputAdmin(admin.ModelAdmin):
    form = CarInputForm
    list_display = ['name', 'year', 'user', 'predict_button']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)

    # Add a button for prediction
    def predict_button(self, obj):
        return format_html(
            '<a class="button" href="{}">Predict</a>',
            f'carinput/carinput/{obj.id}/'
        )
    predict_button.short_description = 'Predict Price'
    predict_button.allow_tags = True

    # Register custom carprice view
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('carinput/carinput/<int:car_id>/', self.admin_site.admin_view(self.predict_view), name='carinput_predict'),
        ]
        return custom_urls + urls

    # The custom prediction view
    def predict_view(self, request, car_id):
        car = self.get_object(request, car_id)

        df = pd.DataFrame([[car.name, car.year, car.km_driven, car.fuel, car.seller_type,
                            car.transmission, car.owner, car.mileage, car.engine,
                            car.max_power, car.seats]],
                          columns=['name','year','km_driven','fuel','seller_type',
                                   'transmission','owner','mileage','engine','max_power','seats'])

        # Encoding mappings
        mappings = {
            'owner': {'First Owner': 1, 'Second Owner': 2, 'Third Owner': 3,
                      'Fourth & Above Owner': 4, 'Test Drive Car': 5},
            'fuel': {'Diesel': 1, 'Petrol': 2, 'LPG': 3, 'CNG': 4},
            'seller_type': {'Individual': 1, 'Dealer': 2, 'Trustmark Dealer': 3},
            'transmission': {'Manual': 1, 'Automatic': 2},
            'name': {n: i+1 for i, n in enumerate(sorted(cars_data['name'].unique()))}
        }

        for col, mapping in mappings.items():
            df[col] = df[col].map(mapping)

        predicted_value = model.predict(df)[0]

        # Optionally, update the model instance
        car.predicted_price = predicted_value
        car.save()

        # Render custom HTML page
        context = dict(
            self.admin_site.each_context(request),
            title='Prediction Result',
            car=car,
            predicted_value=predicted_value
        )
        return TemplateResponse(request, "carprice/result.html", context)