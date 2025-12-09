from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from .forms import PatientRegistrationForm, DoctorRegistrationForm, UserLoginForm, UserProfileForm
from .models import User


def register_patient(request):
    """Handle patient registration."""
    if request.user.is_authenticated:
        return redirect('accounts:redirect_after_login')
    
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Care Point.')
            return redirect('patients:dashboard')
    else:
        form = PatientRegistrationForm()
    
    return render(request, 'accounts/register_patient.html', {'form': form})


def register_doctor(request):
    """Handle doctor registration."""
    if request.user.is_authenticated:
        return redirect('accounts:redirect_after_login')
    
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.info(request, 'Registration successful! Please wait for admin approval before you can access your dashboard.')
            return redirect('accounts:login')
    else:
        form = DoctorRegistrationForm()
    
    return render(request, 'accounts/register_doctor.html', {'form': form})


def register_choice(request):
    """Show registration type selection page."""
    if request.user.is_authenticated:
        return redirect('accounts:redirect_after_login')
    return render(request, 'accounts/register_choice.html')


def user_login(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('accounts:redirect_after_login')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('accounts:redirect_after_login')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def user_logout(request):
    """Handle user logout."""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def redirect_after_login(request):
    """Redirect user to appropriate dashboard based on role."""
    user = request.user
    
    if user.is_superuser or user.is_admin_user:
        return redirect('adminpanel:dashboard')
    elif user.is_doctor:
        if not user.is_approved:
            return redirect('accounts:pending_approval')
        return redirect('doctors:dashboard')
    elif user.is_patient:
        return redirect('patients:dashboard')
    else:
        return redirect('accounts:login')


@login_required
def profile(request):
    """Display and update user profile."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})


def pending_approval(request):
    """Page shown to doctors awaiting approval."""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    if request.user.is_approved:
        return redirect('accounts:redirect_after_login')
    
    return render(request, 'accounts/pending_approval.html')


def home(request):
    """Home page view."""
    if request.user.is_authenticated:
        return redirect('accounts:redirect_after_login')
    return render(request, 'home.html')
