from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


# Create your models here.
class Building(models.Model):
    street = models.CharField(max_length=100)
    number = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=6)
    city = models.CharField(max_length=100)
    manager = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Building {self.number}. Administrator of the building: {self.manager}'

    def get_manager(self):
        return f'{self.manager.first_name} {self.manager.last_name}'

    def get_address(self):
        return f'{self.street} {self.number}'

    def get_postal_code(self):
        return f'{self.zip_code} {self.city}'


class Apartment(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, default=None, on_delete=models.CASCADE, blank=True, null=True)
    floor = models.IntegerField()
    number = models.IntegerField()
    no_residents = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return f'{self.building.street} {self.building.number} m. {self.number}'
