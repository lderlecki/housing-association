from django.contrib import admin
from django.urls import path, include

# from housing import views as housing_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('buildings.urls')),

]
