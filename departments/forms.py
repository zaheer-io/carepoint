from django import forms
from .models import Department


class DepartmentForm(forms.ModelForm):
    """Form for creating/updating departments."""
    
    class Meta:
        model = Department
        fields = ['name', 'description', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
