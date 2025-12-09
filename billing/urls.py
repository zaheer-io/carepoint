from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('payment/<str:order_type>/<int:order_id>/', views.payment, name='payment'),
    path('verify/', views.verify_payment, name='verify_payment'),
    path('success/<int:invoice_id>/', views.payment_success, name='payment_success'),
    path('failure/', views.payment_failure, name='payment_failure'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('webhook/', views.razorpay_webhook, name='razorpay_webhook'),
]
