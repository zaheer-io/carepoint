from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'department', 'scheduled_datetime', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'department', 'scheduled_datetime')
    search_fields = ('patient__user__username', 'doctor__user__username', 'reason')
    date_hierarchy = 'scheduled_datetime'
    list_editable = ('status', 'payment_status')
