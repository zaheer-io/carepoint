from django.contrib import admin
from .models import Invoice

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'invoice_type', 'amount', 'status', 'paid_at', 'created_at')
    list_filter = ('status', 'invoice_type', 'created_at')
    search_fields = ('patient__user__username', 'razorpay_payment_id', 'razorpay_order_id')
    date_hierarchy = 'created_at'
    list_editable = ('status',)
