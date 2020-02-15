from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from buildings.models import Apartment, Building
from .forms import UserRegisterForm, UserUpdateForm


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username') 
            messages.success(request, f'Your account has been created!')
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
            print(request.POST)
            messages.success(request, 'You have succesfully registered a house!')
        
        if 'update' in request.POST:
            u_form = UserUpdateForm(request.POST, instance=user)

            if u_form.is_valid():
                u_form.save()
                messages.success(request, 'Your account has been updated!')
                return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=user)

    buildings = Building.objects.all()
    apartments = Apartment.objects.all()
    context = {'u_form': u_form,
               'allBuildings': buildings,
               'allApartments': apartments}

    return render(request, 'users/profile.html', context)
