from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta

from accounts.decorators import admin_required
from accounts.models import User
from departments.models import Department
from departments.forms import DepartmentForm
from doctors.models import DoctorProfile
from doctors.forms import DoctorProfileForm
from patients.models import PatientProfile
from appointments.models import Appointment
from pharmacy.models import Medicine, PharmacyOrder
from pharmacy.forms import MedicineForm
from billing.models import Invoice


@admin_required
def dashboard(request):
    """Admin dashboard with overview stats."""
    today = timezone.now().date()
    this_month = today.replace(day=1)
    
    # Stats
    total_doctors = User.objects.filter(role=User.Role.DOCTOR).count()
    pending_doctors = User.objects.filter(role=User.Role.DOCTOR, is_approved=False).count()
    total_patients = User.objects.filter(role=User.Role.PATIENT).count()
    
    # Appointments
    today_appointments = Appointment.objects.filter(scheduled_datetime__date=today).count()
    total_appointments = Appointment.objects.count()
    
    # Revenue
    total_revenue = Invoice.objects.filter(status='paid').aggregate(
        total=Sum('amount')
    )['total'] or 0
    monthly_revenue = Invoice.objects.filter(
        status='paid',
        paid_at__date__gte=this_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Recent activity
    recent_appointments = Appointment.objects.order_by('-created_at')[:5]
    pending_doctor_approvals = User.objects.filter(
        role=User.Role.DOCTOR,
        is_approved=False
    ).order_by('-date_joined')[:5]
    
    context = {
        'total_doctors': total_doctors,
        'pending_doctors': pending_doctors,
        'total_patients': total_patients,
        'today_appointments': today_appointments,
        'total_appointments': total_appointments,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'recent_appointments': recent_appointments,
        'pending_doctor_approvals': pending_doctor_approvals,
    }
    return render(request, 'adminpanel/dashboard.html', context)


# Department Management
@admin_required
def department_list(request):
    """List all departments."""
    departments = Department.objects.annotate(
        num_doctors=Count('doctors')
    ).order_by('name')
    
    context = {
        'departments': departments,
    }
    return render(request, 'adminpanel/departments/list.html', context)


@admin_required
def department_create(request):
    """Create a new department."""
    if request.method == 'POST':
        form = DepartmentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department created successfully!')
            return redirect('adminpanel:department_list')
    else:
        form = DepartmentForm()
    
    context = {
        'form': form,
        'title': 'Create Department',
    }
    return render(request, 'adminpanel/departments/form.html', context)


@admin_required
def department_edit(request, pk):
    """Edit a department."""
    department = get_object_or_404(Department, pk=pk)
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, request.FILES, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully!')
            return redirect('adminpanel:department_list')
    else:
        form = DepartmentForm(instance=department)
    
    context = {
        'form': form,
        'title': 'Edit Department',
        'department': department,
    }
    return render(request, 'adminpanel/departments/form.html', context)


@admin_required
def department_delete(request, pk):
    """Delete a department."""
    department = get_object_or_404(Department, pk=pk)
    
    if request.method == 'POST':
        department.delete()
        messages.success(request, 'Department deleted successfully!')
        return redirect('adminpanel:department_list')
    
    context = {
        'department': department,
    }
    return render(request, 'adminpanel/departments/delete.html', context)


# Doctor Management
@admin_required
def doctor_list(request):
    """List all doctors."""
    status_filter = request.GET.get('status', '')
    
    doctors = DoctorProfile.objects.select_related('user', 'department')
    
    if status_filter == 'pending':
        doctors = doctors.filter(user__is_approved=False)
    elif status_filter == 'approved':
        doctors = doctors.filter(user__is_approved=True)
    
    doctors = doctors.order_by('-user__date_joined')
    
    context = {
        'doctors': doctors,
        'status_filter': status_filter,
    }
    return render(request, 'adminpanel/doctors/list.html', context)


@admin_required
def doctor_detail(request, pk):
    """View doctor details."""
    doctor = get_object_or_404(DoctorProfile, pk=pk)
    
    # Get doctor stats
    total_appointments = Appointment.objects.filter(doctor=doctor).count()
    completed_appointments = Appointment.objects.filter(doctor=doctor, status='completed').count()
    pending_appointments = Appointment.objects.filter(doctor=doctor, status='pending').count()
    cancelled_appointments = Appointment.objects.filter(doctor=doctor, status='cancelled').count()
    
    context = {
        'doctor': doctor,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'pending_appointments': pending_appointments,
        'cancelled_appointments': cancelled_appointments,
    }
    return render(request, 'adminpanel/doctors/detail.html', context)


@admin_required
def doctor_approve(request, pk):
    """Approve a doctor."""
    doctor = get_object_or_404(DoctorProfile, pk=pk)
    
    doctor.user.is_approved = True
    doctor.user.save()
    
    messages.success(request, f'Dr. {doctor.user.get_full_name()} has been approved!')
    return redirect('adminpanel:doctor_detail', pk=pk)


@admin_required
def doctor_reject(request, pk):
    """Reject/unapprove a doctor."""
    doctor = get_object_or_404(DoctorProfile, pk=pk)
    
    doctor.user.is_approved = False
    doctor.user.save()
    
    messages.warning(request, f'Dr. {doctor.user.get_full_name()} has been unapproved.')
    return redirect('adminpanel:doctor_detail', pk=pk)


@admin_required
def doctor_edit(request, pk):
    """Edit doctor profile."""
    doctor = get_object_or_404(DoctorProfile, pk=pk)
    
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Doctor profile updated successfully!')
            return redirect('adminpanel:doctor_detail', pk=pk)
    else:
        form = DoctorProfileForm(instance=doctor)
    
    context = {
        'form': form,
        'doctor': doctor,
    }
    return render(request, 'adminpanel/doctors/edit.html', context)


# Patient Management
@admin_required
def patient_list(request):
    """List all patients."""
    # Only show users with patient role (exclude admins/staff completely)
    patients = PatientProfile.objects.select_related('user').filter(
        user__role=User.Role.PATIENT,
        user__is_superuser=False,
        user__is_staff=False
    ).order_by('-user__date_joined')
    
    context = {
        'patients': patients,
    }
    return render(request, 'adminpanel/patients/list.html', context)


@admin_required
def patient_detail(request, pk):
    """View patient details."""
    patient = get_object_or_404(PatientProfile, pk=pk)
    
    appointments = Appointment.objects.filter(patient=patient).order_by('-scheduled_datetime')[:10]
    
    context = {
        'patient': patient,
        'appointments': appointments,
    }
    return render(request, 'adminpanel/patients/detail.html', context)


# Appointment Management
@admin_required
def appointment_list(request):
    """List all appointments."""
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    
    appointments = Appointment.objects.select_related('patient', 'doctor', 'department')
    
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    if date_filter == 'today':
        appointments = appointments.filter(scheduled_datetime__date=timezone.now().date())
    elif date_filter == 'upcoming':
        appointments = appointments.filter(scheduled_datetime__date__gte=timezone.now().date())
    
    appointments = appointments.order_by('-scheduled_datetime')[:100]
    
    context = {
        'appointments': appointments,
        'status_filter': status_filter,
        'date_filter': date_filter,
    }
    return render(request, 'adminpanel/appointments/list.html', context)


@admin_required
def appointment_detail(request, pk):
    """View appointment details."""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    context = {
        'appointment': appointment,
    }
    return render(request, 'adminpanel/appointments/detail.html', context)


@admin_required
def appointment_cancel(request, pk):
    """Cancel an appointment (admin override)."""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled.')
        return redirect('adminpanel:appointment_detail', pk=pk)
    
    context = {
        'appointment': appointment,
    }
    return render(request, 'adminpanel/appointments/cancel.html', context)


# Medicine Management
@admin_required
def medicine_list(request):
    """List all medicines."""
    medicines = Medicine.objects.order_by('name')
    
    context = {
        'medicines': medicines,
    }
    return render(request, 'adminpanel/pharmacy/medicine_list.html', context)


@admin_required
def medicine_create(request):
    """Create a new medicine."""
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine added successfully!')
            return redirect('adminpanel:medicine_list')
    else:
        form = MedicineForm()
    
    context = {
        'form': form,
        'title': 'Add Medicine',
    }
    return render(request, 'adminpanel/pharmacy/medicine_form.html', context)


@admin_required
def medicine_edit(request, pk):
    """Edit a medicine."""
    medicine = get_object_or_404(Medicine, pk=pk)
    
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine updated successfully!')
            return redirect('adminpanel:medicine_list')
    else:
        form = MedicineForm(instance=medicine)
    
    context = {
        'form': form,
        'title': 'Edit Medicine',
        'medicine': medicine,
    }
    return render(request, 'adminpanel/pharmacy/medicine_form.html', context)


@admin_required
def medicine_delete(request, pk):
    """Delete a medicine."""
    medicine = get_object_or_404(Medicine, pk=pk)
    
    if request.method == 'POST':
        medicine.delete()
        messages.success(request, 'Medicine deleted successfully!')
        return redirect('adminpanel:medicine_list')
    
    context = {
        'medicine': medicine,
    }
    return render(request, 'adminpanel/pharmacy/medicine_delete.html', context)


# Pharmacy Orders
@admin_required
def pharmacy_order_list(request):
    """List all pharmacy orders."""
    status_filter = request.GET.get('status', '')
    
    orders = PharmacyOrder.objects.select_related('patient')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    orders = orders.order_by('-created_at')[:100]
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
    }
    return render(request, 'adminpanel/pharmacy/order_list.html', context)


@admin_required
def pharmacy_order_detail(request, pk):
    """View pharmacy order details."""
    order = get_object_or_404(PharmacyOrder, pk=pk)
    
    context = {
        'order': order,
    }
    return render(request, 'adminpanel/pharmacy/order_detail.html', context)


@admin_required
def pharmacy_order_update_status(request, pk):
    """Update pharmacy order status."""
    order = get_object_or_404(PharmacyOrder, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(PharmacyOrder.Status.choices):
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to {order.get_status_display()}.')
    
    return redirect('adminpanel:pharmacy_order_detail', pk=pk)
