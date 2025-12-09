from django import forms
from .models import DoctorProfile, Prescription, PrescriptionItem


class DoctorProfileForm(forms.ModelForm):
    """Form for updating doctor profile."""
    
    class Meta:
        model = DoctorProfile
        fields = [
            'department', 'qualifications', 'specialization',
            'experience_years', 'bio', 'consultation_fee',
            'available_from', 'available_to'
        ]
        widgets = {
            'department': forms.Select(attrs={'class': 'form-control'}),
            'qualifications': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_from': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'available_to': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }


class PrescriptionForm(forms.ModelForm):
    """Form for creating prescriptions."""
    
    class Meta:
        model = Prescription
        fields = ['diagnosis', 'notes']
        widgets = {
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PrescriptionItemForm(forms.ModelForm):
    """Form for adding prescription items."""
    
    class Meta:
        model = PrescriptionItem
        fields = ['medicine_name', 'dosage', 'frequency', 'duration', 'instructions']
        widgets = {
            'medicine_name': forms.TextInput(attrs={'class': 'form-control'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control'}),
            'frequency': forms.TextInput(attrs={'class': 'form-control'}),
            'duration': forms.TextInput(attrs={'class': 'form-control'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


PrescriptionItemFormSet = forms.inlineformset_factory(
    Prescription,
    PrescriptionItem,
    form=PrescriptionItemForm,
    extra=1,  # Start with 1 medicine, user can add more dynamically
    can_delete=True,
    min_num=0,
    validate_min=False,
)

