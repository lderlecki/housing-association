from io import BytesIO

import six
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string, get_template
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from xhtml2pdf import pisa


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.profile.email_is_active)


generate_token = TokenGenerator()


def generate_activation_email(request, user):
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
    return email


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None



