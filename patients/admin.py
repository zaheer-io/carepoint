from django.contrib import admin
from .models import PatientProfile

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'gender', 'blood_group', 'emergency_contact_phone')
    list_filter = ('gender', 'blood_group', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__phone')
