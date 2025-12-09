from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('appointments/book/', views.book_appointment, name='book_appointment'),
    path('appointments/', views.appointment_history, name='appointment_history'),
    path('appointments/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<int:pk>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('prescriptions/', views.prescription_list, name='prescription_list'),
    path('prescriptions/<int:pk>/', views.prescription_detail, name='prescription_detail'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # AJAX endpoints
    path('api/doctors-by-department/', views.get_doctors_by_department, name='get_doctors_by_department'),
]
