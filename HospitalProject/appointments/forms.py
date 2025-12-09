from django import forms
from django.utils import timezone
from .models import Appointment
from departments.models import Department
from doctors.models import DoctorProfile


class AppointmentBookingForm(forms.ModelForm):
    """Form for booking appointments."""
    
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'department-select'}),
        empty_label="Select Department"
    )
    
    doctor = forms.ModelChoiceField(
        queryset=DoctorProfile.objects.filter(user__is_approved=True),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'doctor-select'}),
        empty_label="Select Doctor"
    )
    
    scheduled_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': timezone.now().date().isoformat()
        })
    )
    
    scheduled_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    
    class Meta:
        model = Appointment
        fields = ['department', 'doctor', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Briefly describe the reason for your visit'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initially show all approved doctors; filter will be done via JS
        self.fields['doctor'].queryset = DoctorProfile.objects.filter(
            user__is_approved=True,
            user__is_active=True
        )
    
    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        scheduled_date = cleaned_data.get('scheduled_date')
        scheduled_time = cleaned_data.get('scheduled_time')
        
        if doctor and scheduled_date and scheduled_time:
            # Combine date and time
            from datetime import datetime
            scheduled_datetime = datetime.combine(scheduled_date, scheduled_time)
            scheduled_datetime = timezone.make_aware(scheduled_datetime)
            
            # Check availability
            available, message = Appointment.check_availability(doctor, scheduled_datetime)
            if not available:
                raise forms.ValidationError(message)
            
            cleaned_data['scheduled_datetime'] = scheduled_datetime
        
        return cleaned_data
