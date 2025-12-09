from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom User model with role-based authentication."""
    
    class Role(models.TextChoices):
        PATIENT = 'patient', 'Patient'
        DOCTOR = 'doctor', 'Doctor'
        ADMIN = 'admin', 'Admin'
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PATIENT
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_approved = models.BooleanField(
        default=True,
        help_text='For doctors: set to False until admin approves'
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def save(self, *args, **kwargs):
        # Force Admin role for superusers to prevent them being treated as patients
        if self.is_superuser:
            self.role = self.Role.ADMIN
            
        # Doctors need approval by default
        if self.role == self.Role.DOCTOR and self._state.adding:
            self.is_approved = False
        super().save(*args, **kwargs)
    
    @property
    def is_patient(self):
        return self.role == self.Role.PATIENT
    
    @property
    def is_doctor(self):
        return self.role == self.Role.DOCTOR
    
    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN or self.is_superuser
