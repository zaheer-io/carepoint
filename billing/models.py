from django.db import models
from django.conf import settings


class Invoice(models.Model):
    """Invoice model for payments."""
    
    class InvoiceType(models.TextChoices):
        APPOINTMENT = 'appointment', 'Appointment'
        PHARMACY = 'pharmacy', 'Pharmacy Order'
    
    class Status(models.TextChoices):
        UNPAID = 'unpaid', 'Unpaid'
        PAID = 'paid', 'Paid'
        REFUNDED = 'refunded', 'Refunded'
        FAILED = 'failed', 'Failed'
    
    patient = models.ForeignKey(
        'patients.PatientProfile',
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    invoice_type = models.CharField(
        max_length=20,
        choices=InvoiceType.choices
    )
    
    # Link to appointment or pharmacy order
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices'
    )
    pharmacy_order = models.ForeignKey(
        'pharmacy.PharmacyOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices'
    )
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UNPAID
    )
    
    # Razorpay fields
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice #{self.pk} - {self.get_invoice_type_display()} - ₹{self.amount}"
    
    @property
    def amount_in_paise(self):
        """Convert amount to paise for Razorpay."""
        return int(self.amount * 100)
