from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse

from accounts.decorators import patient_required
from .models import PatientProfile
from .forms import PatientProfileForm
from appointments.models import Appointment
from appointments.forms import AppointmentBookingForm
from doctors.models import Prescription, DoctorProfile
from departments.models import Department


@patient_required
def dashboard(request):
    """Patient dashboard with overview."""
    patient = request.user.patient_profile
    today = timezone.now().date()
    
    # Get upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        patient=patient,
        scheduled_datetime__date__gte=today,
        status__in=['pending', 'confirmed']
    ).order_by('scheduled_datetime')[:5]
    
    # Get recent prescriptions
    recent_prescriptions = Prescription.objects.filter(
        appointment__patient=patient
    ).order_by('-created_at')[:5]
    
    # Stats
    total_appointments = Appointment.objects.filter(patient=patient).count()
    completed_appointments = Appointment.objects.filter(
        patient=patient,
        status='completed'
    ).count()
    
    context = {
        'patient': patient,
        'upcoming_appointments': upcoming_appointments,
        'recent_prescriptions': recent_prescriptions,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
    }
    return render(request, 'patients/dashboard.html', context)


@patient_required
def book_appointment(request):
    """Book a new appointment."""
    patient = request.user.patient_profile
    
    # Check if profile is complete before allowing booking
    if not patient.is_profile_complete:
        messages.warning(request, 'Please complete your profile (date of birth, gender, and emergency contact) before booking an appointment.')
        return redirect('patients:edit_profile')
    
    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            appointment.scheduled_datetime = form.cleaned_data['scheduled_datetime']
            appointment.save()
            messages.success(request, 'Appointment booked successfully! Waiting for doctor confirmation.')
            return redirect('patients:appointment_detail', pk=appointment.pk)
    else:
        form = AppointmentBookingForm()
    
    departments = Department.objects.filter(is_active=True)
    
    context = {
        'form': form,
        'departments': departments,
    }
    return render(request, 'patients/book_appointment.html', context)


@patient_required
def appointment_history(request):
    """View appointment history."""
    patient = request.user.patient_profile
    status_filter = request.GET.get('status', '')
    
    appointments = Appointment.objects.filter(patient=patient)
    
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    appointments = appointments.order_by('-scheduled_datetime')
    
    context = {
        'appointments': appointments,
        'status_filter': status_filter,
    }
    return render(request, 'patients/appointment_history.html', context)


@patient_required
def appointment_detail(request, pk):
    """View appointment details."""
    patient = request.user.patient_profile
    appointment = get_object_or_404(Appointment, pk=pk, patient=patient)
    
    context = {
        'appointment': appointment,
    }
    return render(request, 'patients/appointment_detail.html', context)


@patient_required
def cancel_appointment(request, pk):
    """Cancel an appointment."""
    patient = request.user.patient_profile
    appointment = get_object_or_404(Appointment, pk=pk, patient=patient)
    
    if appointment.can_cancel:
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled successfully.')
    else:
        messages.error(request, 'This appointment cannot be cancelled.')
    
    return redirect('patients:appointment_detail', pk=pk)


@patient_required
def prescription_list(request):
    """View all prescriptions."""
    patient = request.user.patient_profile
    
    prescriptions = Prescription.objects.filter(
        appointment__patient=patient
    ).order_by('-created_at')
    
    context = {
        'prescriptions': prescriptions,
    }
    return render(request, 'patients/prescription_list.html', context)


@patient_required
def prescription_detail(request, pk):
    """View prescription details."""
    patient = request.user.patient_profile
    prescription = get_object_or_404(
        Prescription,
        pk=pk,
        appointment__patient=patient
    )
    
    context = {
        'prescription': prescription,
    }
    return render(request, 'patients/prescription_detail.html', context)


@patient_required
def edit_profile(request):
    """Edit patient profile."""
    patient = request.user.patient_profile
    
    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('patients:dashboard')
    else:
        form = PatientProfileForm(instance=patient)
    
    context = {
        'form': form,
    }
    return render(request, 'patients/edit_profile.html', context)


def get_doctors_by_department(request):
    """AJAX endpoint to get doctors by department."""
    department_id = request.GET.get('department_id')
    
    if department_id:
        doctors = DoctorProfile.objects.filter(
            department_id=department_id,
            user__is_approved=True,
            user__is_active=True
        ).values('id', 'user__first_name', 'user__last_name', 'specialization', 'consultation_fee')
        
        doctor_list = [
            {
                'id': doc['id'],
                'name': f"Dr. {doc['user__first_name']} {doc['user__last_name']}",
                'specialization': doc['specialization'],
                'fee': str(doc['consultation_fee'])
            }
            for doc in doctors
        ]
        return JsonResponse({'doctors': doctor_list})
    
    return JsonResponse({'doctors': []})
