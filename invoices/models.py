from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from buildings.models import Apartment


'''
avg water usage pp 0.15 m3

'''


def get_invoice_name(apartment):
    last_invoice = Invoice.objects.filter(id=apartment.get_number()).order_by('id').last()
    date = datetime.now()
    if not last_invoice:
        return f'B{apartment.building_id}A{apartment.get_number()}/{date.year}/{date.month}/0001'
    order_num = last_invoice.order_number
    new_invoice_no = f'B{apartment.building_id}A{apartment.get_number()}/{date.year}/{date.month}/{order_num}'
    return new_invoice_no


def get_due_date():
    return datetime.now() + timedelta(14)


def increment_invoice_number():
    """Calculate order number for invoice"""
    last_invoice = Invoice.objects.all().order_by('id').last()
    if not last_invoice:
        return '0001'
    old_number = last_invoice.order_number
    number = str(int(old_number) + 1)
    new_invoice_no = '0' * (len(old_number) - len(str(int(number) + 1))) + number
    return new_invoice_no


class Fees(models.Model):
    """Prices for each service
    hot_water: 16.49 PLN/m3
    cold_water: 4.29 PLN/m3
    sewage: 4.38 PLN/m3
    electricity: 0.621 PLN/kWh
    gas: 0.1175 PLN/kWh
    service_charge_insulated: 3.62 / m2
    service_charge_non_insulated: 3.33 /m2
    """
    hot_water = models.DecimalField(max_digits=100, decimal_places=4, default=16.49)
    cold_water = models.DecimalField(max_digits=100, decimal_places=4, default=4.29)
    sewage = models.DecimalField(max_digits=100, decimal_places=4, default=4.38)
    electricity = models.DecimalField(max_digits=100, decimal_places=4, default=0.621)
    gas = models.DecimalField(max_digits=100, decimal_places=4, default=0.1175)
    # heating = models.DecimalField(max_digits=100, decimal_places=4, default=0.09)
    repair_fund = models.DecimalField(max_digits=100, decimal_places=4, default=0.09)
    service_charge_insulated = models.DecimalField(max_digits=100, decimal_places=2, default=3.62)
    service_charge_non_insulated = models.DecimalField(max_digits=100, decimal_places=2, default=3.33)

    def save(self, *args, **kwargs):
        if not self.pk and Fees.objects.exists():
            raise ValidationError('There can be only one scheme with Fees. Please update the existing one.')
        return super(Fees, self).save(*args, **kwargs)


class DefaultServiceUsagePP(models.Model):
    """Poland average usage of each of the services per person
    hot_water: 0.07 m3 / day per person
    cold_water: 0.09 m3/ day per person
    sewage: 4.38 for for 1m3 of water
    electricity: 29.35 kWh / m2
    gas: 7.7 m3 / m2
    """
    hot_water = models.DecimalField(max_digits=100, decimal_places=2, default=0.07)
    cold_water = models.DecimalField(max_digits=100, decimal_places=2, default=0.09)
    sewage = models.DecimalField(max_digits=100, decimal_places=2, default=0.09)
    electricity = models.DecimalField(max_digits=100, decimal_places=2, default=29.35)
    gas = models.DecimalField(max_digits=100, decimal_places=2, default=0.09)

    # heating     = models.DecimalField(max_digits=100, decimal_places=2, default=0.09)

    def save(self, *args, **kwargs):
        if not self.pk and DefaultServiceUsagePP.objects.exists():
            raise ValidationError('There can be only one scheme with default values for invoice.\
                                   Please update the existing one.')
        return super(DefaultServiceUsagePP, self).save(*args, **kwargs)


class InvoiceItems(models.Model):
    invoice     = models.ForeignKey('Invoice', on_delete=models.CASCADE, null=True, blank=True)
    hot_water   = models.DecimalField(max_digits=100, decimal_places=2, default=0.0,
                                      validators=[MinValueValidator(Decimal('0.01'))])
    cold_water  = models.DecimalField(max_digits=100, decimal_places=2, default=0.0,
                                      validators=[MinValueValidator(Decimal('0.01'))])
    sewage      = models.DecimalField(max_digits=100, decimal_places=2, default=0.0,
                                      validators=[MinValueValidator(Decimal('0.01'))])
    electricity = models.DecimalField(max_digits=100, decimal_places=2, default=0.0,
                                      validators=[MinValueValidator(Decimal('0.01'))])
    gas         = models.DecimalField(max_digits=100, decimal_places=2, default=0.0,
                                      validators=[MinValueValidator(Decimal('0.01'))])
    # heating     = models.DecimalField(max_digits=100, decimal_places=2, default=0.0,
    #                                     validators=[MinValueValidator(Decimal('0.01'))])
    repair_fund = models.DecimalField(max_digits=100, decimal_places=2, default=0.0,
                                      validators=[MinValueValidator(Decimal('0.01'))])

    # def


class Invoice(models.Model):
    AWAITING_CONFIRMATION = 1
    AWAITING_PAYMENT      = 2
    FINISHED              = 3
    PAYMENT_NOT_RECEIVED  = 4

    INVOICE_STATUS_CHOICES = [
        (AWAITING_CONFIRMATION, 'Awaiting confirmation'),
        (AWAITING_PAYMENT, 'Awaiting payment'),
        (FINISHED, 'Finished'),
        (PAYMENT_NOT_RECEIVED, 'Payment failed'),
    ]
    related_user      = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    related_apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, null=True, blank=True)
    order_number      = models.CharField(max_length=500, default=increment_invoice_number, null=True, blank=True)
    invoice_no        = models.CharField(max_length=500, default=None, null=True, blank=True)
    invoice_status    = models.IntegerField(choices=INVOICE_STATUS_CHOICES, default=AWAITING_CONFIRMATION, null=True, blank=True)
    date_received     = models.DateField(auto_now_add=True)
    date_due          = models.DateField(default=get_due_date)
    date_paid         = models.DateField(null=True, blank=True)

    def save(self):
        if not self.pk:
            invoice_name = get_invoice_name(self.related_apartment)
            self.invoice_no = invoice_name
        if self.related_apartment.owner != self.related_user:
            raise ValidationError('This apartment is not owned by given user.')

        super().save()
