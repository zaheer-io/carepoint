from django import forms
from .models import PatientProfile


class PatientProfileForm(forms.ModelForm):
    """Form for updating patient profile."""
    
    class Meta:
        model = PatientProfile
        fields = [
            'date_of_birth', 'gender', 'blood_group', 'address',
            'emergency_contact_name', 'emergency_contact_phone',
            'medical_history', 'allergies'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'medical_history': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
