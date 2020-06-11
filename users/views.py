import json
import urllib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import View


from buildings.models import Apartment, Building
from .forms import UserRegisterForm, UserUpdateForm, HousingForm
from .utils import generate_token


def register(request):
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
            domain = get_current_site(request)
            email_subject = 'Activate your Account'
            message = render_to_string('users/activate.html',
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
            email.send()

            messages.success(request, f'Your account has been created! \n\
                                        Please check your inbox and follow the instructions to activate your account.')
            return redirect('login')

    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        if 'save_data' in request.POST:
            u_form = UserUpdateForm(instance=user)
            h_form = HousingForm(request.POST)

            if h_form.is_valid():
                h_form.save(user)
                messages.success(request, 'You have succesfully registered a house!')
                return redirect('profile')

        if 'update' in request.POST:
            u_form = UserUpdateForm(request.POST, instance=user)
            h_form = HousingForm()

            if u_form.is_valid():
                u_form.save()
                messages.success(request, 'Your account has been updated!')
                return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=user)
        h_form = HousingForm()

    context = {
        'u_form': u_form,
        'h_form': h_form,
        }
    return render(request, 'users/profile.html', context)


def move_out(request):
    user_profile = request.user.profile
    apartment = user_profile.apartment
    user_profile.apartment = None
    apartment.owner = None

    apartment.save()
    user_profile.save()

    messages.success(request, 'You have successfully moved out!')
    return redirect('profile')


class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            user = None
        if user and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.add_message(request, messages.INFO, 'You account is now active!')
            return redirect('login')
        return render(request, 'users/activate_failed.html', status=401)

