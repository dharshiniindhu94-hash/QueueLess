
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import PatientRegistrationForm


def register(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = PatientRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Redirect doctor to Doctor Dashboard
            if hasattr(user, 'doctor_profile'):
                return redirect('doctor_dashboard')

            # Redirect other users to Home
            return redirect('home')

    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')
