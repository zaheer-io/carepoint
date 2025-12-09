from django.shortcuts import render, get_object_or_404
from .models import Department


def department_list(request):
    """List all active departments."""
    departments = Department.objects.filter(is_active=True)
    return render(request, 'departments/list.html', {'departments': departments})


def department_detail(request, slug):
    """Show department details with its doctors."""
    department = get_object_or_404(Department, slug=slug, is_active=True)
    doctors = department.active_doctors
    return render(request, 'departments/detail.html', {
        'department': department,
        'doctors': doctors
    })
