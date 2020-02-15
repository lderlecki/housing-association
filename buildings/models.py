from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Building(models.Model):
    street = models.CharField(max_length=100)
    number = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=6)
    city = models.CharField(max_length=100)
    manager = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Building {self.number}. Administrator of the building: {self.manager}'

class Apartment(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    floor = models.IntegerField()
    number = models.IntegerField()
    no_residents = models.IntegerField(default=0)

    def __str__(self):
        return f'Building {self.building.number}, floor {self.floor}, number {self.number}, owner: {self.owner.get_full_name() if self.owner else "None"}'
