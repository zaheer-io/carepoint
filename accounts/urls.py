from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_patient, name='register'),
    path('register/choice/', views.register_choice, name='register_choice'),
    path('register/patient/', views.register_patient, name='register_patient'),
    path('register/doctor/', views.register_doctor, name='register_doctor'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('pending-approval/', views.pending_approval, name='pending_approval'),
    path('redirect/', views.redirect_after_login, name='redirect_after_login'),
]
