from datetime import datetime

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from .models import Invoice, InvoiceItems


class InvoiceFillForm(forms.ModelForm):
    class Meta:
        model = InvoiceItems
        exclude = ('invoice', )

