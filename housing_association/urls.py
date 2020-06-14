from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from users import views as user_views

# from housing import views as housing_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', user_views.register, name='register'),
    path('profile/', login_required(user_views.Profile.as_view()), name='profile'),
    path('profile/moveout/', user_views.move_out, name='move-out'),
    path('login/',
         auth_views.LoginView.as_view(template_name='users/login.html', redirect_authenticated_user=True),
         name='login'),

    path('activate/<uidb64>/<token>/', user_views.ActivateAccountView.as_view(), name='activate'),
    path('set-new-password/<uidb64>/<token>/', user_views.SetNewPasswordView.as_view(), name='set-new-password'),
    path('request-reset-email/', user_views.RequestResetEmailView.as_view(), name='request-reset-email'),
    path('profile/request-new-activation/', user_views.resend_activation_email, name='request-new-activation'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('', include('buildings.urls')),


    path('pdf_view/', user_views.ViewPDF.as_view(), name='pdf_view'),
    path('pdf_download_view/', user_views.DownloadPDF.as_view(), name='pdf_download_view'),
]
