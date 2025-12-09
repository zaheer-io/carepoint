from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Departments
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
    
    # Doctors
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('doctors/<int:pk>/approve/', views.doctor_approve, name='doctor_approve'),
    path('doctors/<int:pk>/reject/', views.doctor_reject, name='doctor_reject'),
    path('doctors/<int:pk>/edit/', views.doctor_edit, name='doctor_edit'),
    
    # Patients
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    
    # Appointments
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<int:pk>/cancel/', views.appointment_cancel, name='appointment_cancel'),
    
    # Pharmacy - Medicines
    path('pharmacy/medicines/', views.medicine_list, name='medicine_list'),
    path('pharmacy/medicines/create/', views.medicine_create, name='medicine_create'),
    path('pharmacy/medicines/<int:pk>/edit/', views.medicine_edit, name='medicine_edit'),
    path('pharmacy/medicines/<int:pk>/delete/', views.medicine_delete, name='medicine_delete'),
    
    # Pharmacy - Orders
    path('pharmacy/orders/', views.pharmacy_order_list, name='pharmacy_order_list'),
    path('pharmacy/orders/<int:pk>/', views.pharmacy_order_detail, name='pharmacy_order_detail'),
    path('pharmacy/orders/<int:pk>/update-status/', views.pharmacy_order_update_status, name='pharmacy_order_update_status'),
]
