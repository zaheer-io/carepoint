from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(allowed_roles):
    """Decorator to check if user has required role."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to access this page.')
                return redirect('accounts:login')
            
            if request.user.role not in allowed_roles and not request.user.is_superuser:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('accounts:login')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def patient_required(view_func):
    """Decorator to ensure only patients can access the view."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        if not request.user.is_patient:
            messages.error(request, 'Only patients can access this page.')
            return redirect('accounts:login')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def doctor_required(view_func):
    """Decorator to ensure only approved doctors can access the view."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        if not request.user.is_doctor:
            messages.error(request, 'Only doctors can access this page.')
            return redirect('accounts:login')
        
        if not request.user.is_approved:
            messages.warning(request, 'Your account is pending approval. Please wait for admin approval.')
            return redirect('accounts:pending_approval')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Decorator to ensure only admins can access the view."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        if not request.user.is_admin_user:
            messages.error(request, 'Only administrators can access this page.')
            return redirect('accounts:login')
        
        return view_func(request, *args, **kwargs)
    return wrapper
