from django.contrib import admin
from .models import DoctorProfile, Prescription, PrescriptionItem

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'specialization', 'consultation_fee', 'is_available')
    list_filter = ('department', 'specialization')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'specialization')

class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'appointment', 'diagnosis', 'created_at')
    search_fields = ('appointment__patient__user__username', 'diagnosis')
    inlines = [PrescriptionItemInline]

@admin.register(PrescriptionItem)
class PrescriptionItemAdmin(admin.ModelAdmin):
    list_display = ('medicine_name', 'prescription', 'dosage', 'frequency', 'duration')
    search_fields = ('medicine_name', 'prescription__id')
