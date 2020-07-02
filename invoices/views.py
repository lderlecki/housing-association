from django import forms
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import View

from invoices.forms import InvoiceFillForm
from invoices.models import Invoice


class InvoiceView(View):
    form_class = InvoiceFillForm

    def get(self, request):
        service_form = self.form_class()
        context = {
            'form': service_form,
        }
        return render(request, 'invoices/invoice.html', context)

    def post(self, request):
        user = request.user
        if 'submit_invoice' in request.POST:
            service_form = self.form_class(request.POST)
            if service_form.is_valid():
                service_form.save()
                messages.success(request, "Thank you for filling the form. Now it has to be accepted by the building\
                                          's manager")
            else:
                messages.error(request, "Ensure that all values are greater than 0.")
        return redirect('fill-invoice')


class InvoiceManagerConfirmView(View):

    def get(self, request):
        # data =
        return render(request, 'invoices/confirm_invoices.html')
