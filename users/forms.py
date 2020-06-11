from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from buildings.models import Apartment


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(label="First name")
    last_name = forms.CharField(label="Last name")

    class Meta:
        model = User # affected model
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2'] # fields and their order
    
    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = False

        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class HousingForm(forms.ModelForm):
    residents = forms.IntegerField(initial=1)
    apartment = forms.ModelChoiceField(queryset=Apartment.objects.filter(owner=None).order_by('building', 'number'),
                                       empty_label=None,
                                       widget=forms.Select)

    class Meta:
        model = Apartment
        fields = ['residents', 'apartment']

    def clean_residents(self, *args, **kwargs):
        residents = self.cleaned_data.get('residents')
        if residents < 1:
            raise forms.ValidationError("Number of residents must be greater than 0")
        return residents

    def save(self, user):
        residents = self.cleaned_data['residents']
        apartment = self.cleaned_data['apartment']
        apartment.owner = user
        apartment.no_residents = residents
        user.profile.apartment = apartment
        user.save()
        apartment.save()
