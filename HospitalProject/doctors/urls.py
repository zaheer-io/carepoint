from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<int:pk>/confirm/', views.confirm_appointment, name='confirm_appointment'),
    path('appointments/<int:pk>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('appointments/<int:pk>/mark-paid/', views.mark_appointment_paid, name='mark_appointment_paid'),
    path('appointments/<int:pk>/complete/', views.complete_appointment, name='complete_appointment'),
    path('appointments/<int:pk>/prescription/', views.create_prescription, name='create_prescription'),
    path('prescriptions/<int:pk>/', views.view_prescription, name='view_prescription'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]
