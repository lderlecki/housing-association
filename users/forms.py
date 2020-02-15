from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from buildings.models import Apartment


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(label="First name")
    last_name = forms.CharField(label="Last name")

    class Meta:
        model = User #affected model
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2'] # fields and their order
    
    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email']


class HousingForm(forms.Form):
    no_habit = forms.IntegerField(initial=1)
    apartment = forms.ModelChoiceField(queryset=Apartment.objects.all(), empty_label="Choose a house", widget=forms.Select)
