from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class Building(models.Model):
    # INSULATED = 3.62
    # NON_INSULATED = 3.33
    #
    # SERVICE_CHARGE_CHOICES = [
    #     (INSULATED, 'Insulated'),
    #     (NON_INSULATED, 'Non-Insulated'),
    # ]

    street          = models.CharField(max_length=100)
    number          = models.CharField(max_length=100)
    zip_code        = models.CharField(max_length=6)
    city            = models.CharField(max_length=100)
    # service_charge  = models.FloatField(choices=SERVICE_CHARGE_CHOICES, default=INSULATED)
    manager         = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f'Building {self.number}. Administrator of the building: {self.manager}'

    def get_manager(self):
        return f'{self.manager.first_name} {self.manager.last_name}'

    def get_address(self):
        return f'{self.street} {self.number}'

    def get_postal_code(self):
        return f'{self.zip_code} {self.city}'

    def get_number(self):
        return self.number


class Apartment(models.Model):
    building      = models.ForeignKey(Building, on_delete=models.CASCADE)
    owner         = models.ForeignKey(User, default=None, on_delete=models.SET_NULL, blank=True, null=True)
    floor         = models.IntegerField()
    number        = models.IntegerField()
    no_residents  = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    area          = models.FloatField(default=40.0)
    move_in_date  = models.DateField(auto_now_add=False, auto_now=False, default=None, blank=True, null=True)
    move_out_date = models.DateField(auto_now_add=False, auto_now=False, default=None, blank=True, null=True)

    def __str__(self):
        return f'{self.building.street} {self.building.number} m. {self.number}'

    def get_area(self):
        return self.area

    def get_number(self):
        return self.number

# class ApartmentRentHistory(models.Model):
#     apartment = models.ForeignKey(Apartment)
