import json
import threading
import urllib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core import exceptions
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import View

from .decorators import unauthenticated_user
from .forms import (UserRegisterForm,
                    UserUpdateForm,
                    HousingForm,
                    RequestResetPasswordForm,
                    SetNewPassword,
                    )
from .utils import generate_token, generate_activation_email, render_to_pdf  # , data


class EmailThread(threading.Thread):
    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()


@unauthenticated_user
def register(request):
    form = UserRegisterForm()
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Recaptcha Validation
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            data = urllib.parse.urlencode(values).encode()
            req = urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())

            if not result['success']:
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
                return redirect('register')

            user = form.save()
            email = generate_activation_email(request, user)
            EmailThread(email).start()

            messages.success(request, f'Your account has been created! \n\
                                        Please check your inbox and follow the instructions to activate your account.')
            return redirect('login')
    return render(request, 'users/register.html', {'form': form})


class Profile(View):
    def get(self, request):
        u_form = UserUpdateForm(instance=request.user)
        h_form = HousingForm()
        context = {
            'u_form': u_form,
            'h_form': h_form,
        }
        return render(request, 'users/profile.html', context)

    def post(self, request):
        user = request.user
        if 'save_data' in request.POST:
            h_form = HousingForm(request.POST)
            if h_form.is_valid():
                h_form.save(user)
                messages.success(request, 'You have successfully registered a house!')
                return redirect('profile')
            context = {
                'u_form': UserUpdateForm(instance=request.user),
                'h_form': h_form,
            }
            return render(request, 'users/profile.html', context)

        elif 'update' in request.POST:
            u_form = UserUpdateForm(request.POST, instance=user)
            if u_form.is_valid():
                u_form.save()
                messages.success(request, 'Your account has been updated!')
                return redirect('profile')
            context = {
                'u_form': u_form,
                'h_form': HousingForm(),
            }
            return render(request, 'users/profile.html', context)


@login_required
def move_out(request):
    user_profile = request.user.profile
    apartment = user_profile.apartment
    user_profile.apartment = None
    apartment.owner = None

    apartment.save()
    user_profile.save()

    messages.success(request, 'You have successfully moved out!')
    return redirect('profile')


@login_required
def resend_activation_email(request):
    user = request.user
    email = generate_activation_email(request, user)
    EmailThread(email).start()
    messages.success(request, 'Email with activation link has been sent to your email address!')
    return redirect('profile')


class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except exceptions.ObjectDoesNotExist:
            user = None
        if user is not None and generate_token.check_token(user, token):
            user.profile.email_is_active = True
            user.save()
            messages.add_message(request, messages.INFO, 'You account is now active!')
            return redirect('login')

        if user is not None and user.profile.email_is_active:
            messages.info(request, 'Your account is already activated, you can now login to your account.')
            return redirect('login')

        messages.error(request, 'Something went wrong, please request a new activation link.')
        return render(request, 'users/activate_failed.html', status=401)


class RequestResetEmailView(View):
    form_class = RequestResetPasswordForm
    context = {
        'form': form_class,
    }

    def get(self, request):
        return render(request, 'users/request-reset-email.html', self.context)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = User.objects.filter(email=form.cleaned_data.get('email'))
            if not user.exists():
                messages.error(request, 'User with this email does not exist.')
                return render(request, 'users/request-reset-email.html', self.context)
            user = user.first()
            domain = get_current_site(request)
            email_subject = 'Password Reset Request'
            message = render_to_string('users/password-reset.html',
                                       {
                                           'user': user,
                                           'domain': domain.domain,
                                           'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                           'token': generate_token.make_token(user=user),
                                       })
            email = EmailMessage(
                email_subject,
                message,
                settings.EMAIL_HOST_USER,
                [user.email],
            )
            EmailThread(email).start()
            messages.success(request, f'Link with instructions to change your password has been sent! \n\
                                        Check your inbox.')
            return redirect('login')
        # print(form.errors)
        return render(request, 'users/request-reset-email.html', self.context)


class SetNewPasswordView(View):
    form_class = SetNewPassword

    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
            'form': self.form_class,
        }
        return render(request, 'users/set-new-password.html', context)

    def post(self, request, uidb64, token):
        form = self.form_class(request.POST)
        context = {
            'uidb64': uidb64,
            'token': token,
            'form': form,
        }
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except exceptions.ObjectDoesNotExist:
            user = None

        if user is not None and generate_token.check_token(user, token):
            if form.is_valid():
                form.save(user)
                messages.add_message(request, messages.INFO, 'You have successfully changed the password.')
                return redirect('login')
        return render(request, 'users/set-new-password.html', context, status=401)


test_data_pdf = {  # test data
    "company": "Test Housing Association",
    "address": "Street goes here",
    "city": "City goes here",
    "state": "State goes here",
    "zipcode": "And zipcode here",

    "phone": "111-222-333",
    "email": "youremail@domain.com",
    "website": "yourwebsite.com",
}


class ViewPDF(View):
    def get(self, request, *args, **kwargs):
        pdf = render_to_pdf('users/pdf_invoice_template.html', test_data_pdf)
        return HttpResponse(pdf, content_type='application/pdf')


class DownloadPDF(View):
    def get(self, request, *args, **kwargs):
        pdf = render_to_pdf('users/pdf_invoice_template.html', test_data_pdf)
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Invoice_123_test_321.pdf"
        content = f"attachment; filename={filename}"
        response['Content-Disposition'] = content
        return response
