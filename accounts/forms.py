from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class PatientRegistrationForm(UserCreationForm):
    """Registration form for patients."""
    
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.PATIENT
        user.is_approved = True
        if commit:
            user.save()
        return user


class DoctorRegistrationForm(UserCreationForm):
    """Registration form for doctors."""
    
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.DOCTOR
        user.is_approved = False  # Doctors need admin approval
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    """Login form for all users."""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile."""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
