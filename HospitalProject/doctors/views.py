from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from accounts.decorators import doctor_required
from .models import DoctorProfile, Prescription, PrescriptionItem
from .forms import DoctorProfileForm, PrescriptionForm, PrescriptionItemFormSet
from appointments.models import Appointment


@doctor_required
def dashboard(request):
    """Doctor dashboard with overview."""
    doctor = request.user.doctor_profile
    today = timezone.now().date()
    
    # Get appointments
    upcoming_appointments = Appointment.objects.filter(
        doctor=doctor,
        scheduled_datetime__date__gte=today,
        status__in=['pending', 'confirmed']
    ).order_by('scheduled_datetime')[:5]
    
    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        scheduled_datetime__date=today
    ).order_by('scheduled_datetime')
    
    total_appointments = Appointment.objects.filter(doctor=doctor).count()
    completed_appointments = Appointment.objects.filter(
        doctor=doctor,
        status='completed'
    ).count()
    
    context = {
        'doctor': doctor,
        'upcoming_appointments': upcoming_appointments,
        'today_appointments': today_appointments,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
    }
    return render(request, 'doctors/dashboard.html', context)


@doctor_required
def appointment_list(request):
    """List all appointments for the doctor."""
    doctor = request.user.doctor_profile
    status_filter = request.GET.get('status', '')
    
    appointments = Appointment.objects.filter(doctor=doctor)
    
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    appointments = appointments.order_by('-scheduled_datetime')
    
    context = {
        'appointments': appointments,
        'status_filter': status_filter,
    }
    return render(request, 'doctors/appointment_list.html', context)


@doctor_required
def appointment_detail(request, pk):
    """View appointment details."""
    doctor = request.user.doctor_profile
    appointment = get_object_or_404(Appointment, pk=pk, doctor=doctor)
    
    context = {
        'appointment': appointment,
    }
    return render(request, 'doctors/appointment_detail.html', context)


@doctor_required
def confirm_appointment(request, pk):
    """Confirm a pending appointment."""
    doctor = request.user.doctor_profile
    appointment = get_object_or_404(Appointment, pk=pk, doctor=doctor)
    
    if appointment.status == 'pending':
        appointment.status = 'confirmed'
        appointment.save()
        messages.success(request, 'Appointment confirmed successfully!')
    else:
        messages.error(request, 'This appointment cannot be confirmed.')
    
    return redirect('doctors:appointment_detail', pk=pk)


@doctor_required
def cancel_appointment(request, pk):
    """Cancel an appointment."""
    doctor = request.user.doctor_profile
    appointment = get_object_or_404(Appointment, pk=pk, doctor=doctor)
    
    if appointment.status in ['pending', 'confirmed']:
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled successfully!')
    else:
        messages.error(request, 'This appointment cannot be cancelled.')
    
    return redirect('doctors:appointment_detail', pk=pk)


@doctor_required
def complete_appointment(request, pk):
    """Mark appointment as completed."""
    doctor = request.user.doctor_profile
    appointment = get_object_or_404(Appointment, pk=pk, doctor=doctor)
    
    if appointment.status == 'confirmed':
        appointment.status = 'completed'
        appointment.save()
        messages.success(request, 'Appointment completed! You can now write a prescription.')
        return redirect('doctors:create_prescription', pk=pk)
    else:
        messages.error(request, 'This appointment cannot be completed.')
    
    return redirect('doctors:appointment_detail', pk=pk)


@doctor_required
def mark_appointment_paid(request, pk):
    """Mark appointment as paid (offline payment)."""
    doctor = request.user.doctor_profile
    appointment = get_object_or_404(Appointment, pk=pk, doctor=doctor)
    
    # Allow marking as paid if unpaid, regardless of status (as long as not cancelled)
    if appointment.status != 'cancelled' and appointment.payment_status == 'unpaid':
        appointment.payment_status = 'paid'
        appointment.save()
        
        # Create or update invoice
        from billing.models import Invoice
        Invoice.objects.create(
            appointment=appointment,
            patient=appointment.patient,
            invoice_type='appointment',
            amount=doctor.consultation_fee,
            status='paid',
            paid_at=timezone.now()
        )
        messages.success(request, 'Payment marked as received.')
    else:
        messages.error(request, 'Cannot mark payment. Ensure appointment is valid and currently unpaid.')
    
    # Redirect back to where the user came from (e.g. prescription page or appointment detail)
    referer = request.META.get('HTTP_REFERER')
    if referer and 'doctors' in referer:
        return redirect(referer)
    return redirect('doctors:appointment_detail', pk=pk)



@doctor_required
def create_prescription(request, pk):
    """Create prescription for completed appointment."""
    doctor = request.user.doctor_profile
    appointment = get_object_or_404(Appointment, pk=pk, doctor=doctor)
    
    if appointment.status != 'completed':
        messages.error(request, 'Prescription can only be created for completed appointments.')
        return redirect('doctors:appointment_detail', pk=pk)
    
    # Check if prescription already exists
    if hasattr(appointment, 'prescription'):
        messages.info(request, 'A prescription already exists for this appointment.')
        return redirect('doctors:view_prescription', pk=appointment.prescription.pk)
    
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.appointment = appointment
            prescription.save()
            
            # Handle prescription items
            formset = PrescriptionItemFormSet(request.POST, instance=prescription)
            if formset.is_valid():
                formset.save()
                messages.success(request, 'Prescription created successfully!')
                return redirect('doctors:view_prescription', pk=prescription.pk)
    else:
        form = PrescriptionForm()
        formset = PrescriptionItemFormSet()
    
    context = {
        'form': form,
        'formset': formset,
        'appointment': appointment,
    }
    return render(request, 'doctors/create_prescription.html', context)


@doctor_required
def view_prescription(request, pk):
    """View a prescription."""
    prescription = get_object_or_404(Prescription, pk=pk)
    
    # Verify this prescription belongs to the doctor
    if prescription.appointment.doctor != request.user.doctor_profile:
        messages.error(request, 'You do not have access to this prescription.')
        return redirect('doctors:dashboard')
    
    context = {
        'prescription': prescription,
    }
    return render(request, 'doctors/view_prescription.html', context)


@doctor_required
def edit_profile(request):
    """Edit doctor profile."""
    doctor = request.user.doctor_profile
    
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('doctors:dashboard')
    else:
        form = DoctorProfileForm(instance=doctor)
    
    context = {
        'form': form,
    }
    return render(request, 'doctors/edit_profile.html', context)
