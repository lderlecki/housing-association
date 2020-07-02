from django.db import models
from django.contrib.auth.models import User
from buildings.models import Apartment


# Create your models here.
class Profile(models.Model):
    user            = models.OneToOneField(User, on_delete=models.CASCADE)
    apartment       = models.OneToOneField(Apartment, on_delete=models.SET_NULL, blank=True, null=True)
    email_is_active = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} Profile'
