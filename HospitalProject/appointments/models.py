from django.db import models
from django.conf import settings


class Appointment(models.Model):
    """Appointment booking model."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'
        NO_SHOW = 'no_show', 'No Show'
    
    class PaymentStatus(models.TextChoices):
        UNPAID = 'unpaid', 'Unpaid'
        PAID = 'paid', 'Paid'
        REFUNDED = 'refunded', 'Refunded'
    
    patient = models.ForeignKey(
        'patients.PatientProfile',
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    doctor = models.ForeignKey(
        'doctors.DoctorProfile',
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        related_name='appointments'
    )
    scheduled_datetime = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID
    )
    reason = models.TextField(blank=True, help_text="Reason for visit")
    notes = models.TextField(blank=True, help_text="Additional notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_datetime']
    
    def __str__(self):
        return f"{self.patient} with {self.doctor} on {self.scheduled_datetime.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def is_upcoming(self):
        from django.utils import timezone
        return self.scheduled_datetime > timezone.now()
    
    @property
    def can_cancel(self):
        """Check if appointment can be cancelled by patient."""
        from django.utils import timezone
        # Patient can only cancel if status is pending and appointment is in the future
        # Once doctor confirms, patient cannot cancel
        return (
            self.status == self.Status.PENDING and
            self.scheduled_datetime > timezone.now()
        )
    
    @classmethod
    def check_availability(cls, doctor, datetime_slot, exclude_appointment=None):
        """Check if the doctor is available at the given datetime."""
        from django.utils import timezone
        from datetime import timedelta
        
        # Check if slot is in the past
        if datetime_slot < timezone.now():
            return False, "Cannot book appointments in the past."
        
        # Check for overlapping appointments
        start_time = datetime_slot
        end_time = datetime_slot + timedelta(minutes=30)
        
        overlapping = cls.objects.filter(
            doctor=doctor,
            scheduled_datetime__lt=end_time,
            scheduled_datetime__gte=start_time - timedelta(minutes=30),
            status__in=[cls.Status.PENDING, cls.Status.CONFIRMED]
        )
        
        if exclude_appointment:
            overlapping = overlapping.exclude(pk=exclude_appointment.pk)
        
        if overlapping.exists():
            return False, "This time slot is not available."
        
        return True, "Available"

    @property
    def payment_details(self):
        """Return payment method and status details."""
        if self.payment_status == self.PaymentStatus.PAID:
            invoice = self.invoices.filter(status='paid').last()
            if invoice:
                if invoice.razorpay_payment_id:
                    return {'method': 'Online', 'label': 'Online Payment', 'css': 'info'}
                else:
                    return {'method': 'Offline', 'label': 'Cash / Offline', 'css': 'secondary'}
            return {'method': 'Unknown', 'label': 'Paid', 'css': 'success'}
        return {'method': 'Unpaid', 'label': 'Unpaid', 'css': 'warning'}
