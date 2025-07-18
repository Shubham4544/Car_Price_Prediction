from django.db import models
from django.contrib.auth.models import User

class CarInput(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    year = models.IntegerField()
    km_driven = models.IntegerField()
    fuel = models.CharField(max_length=50)
    seller_type = models.CharField(max_length=50)
    transmission = models.CharField(max_length=50)
    owner = models.CharField(max_length=50)
    mileage = models.FloatField()
    engine = models.FloatField()
    max_power = models.FloatField()
    seats = models.IntegerField()
    predicted_price = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"
