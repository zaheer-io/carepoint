from django.db import models
from django.conf import settings


class DoctorProfile(models.Model):
    """Extended profile for doctors."""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctors'
    )
    qualifications = models.CharField(max_length=200, blank=True)
    specialization = models.CharField(max_length=100, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True)
    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=500.00
    )
    available_from = models.TimeField(null=True, blank=True)
    available_to = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username}"
    
    @property
    def full_name(self):
        return f"Dr. {self.user.get_full_name() or self.user.username}"
    
    @property
    def is_available(self):
        return self.user.is_approved and self.user.is_active


class Prescription(models.Model):
    """Prescription written by doctor for a patient."""
    
    appointment = models.OneToOneField(
        'appointments.Appointment',
        on_delete=models.CASCADE,
        related_name='prescription'
    )
    diagnosis = models.TextField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Prescription for {self.appointment.patient.user.username} - {self.created_at.date()}"


class PrescriptionItem(models.Model):
    """Individual medicine in a prescription."""
    
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='items'
    )
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)  # e.g., "2 times a day"
    duration = models.CharField(max_length=100)  # e.g., "7 days"
    instructions = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.medicine_name} - {self.dosage}"
