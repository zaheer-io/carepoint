import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from accounts.decorators import patient_required
from .models import Invoice
from appointments.models import Appointment
from pharmacy.models import PharmacyOrder


# Initialize Razorpay client
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


@patient_required
def payment(request, order_type, order_id):
    """Initiate payment for appointment or pharmacy order."""
    patient = request.user.patient_profile
    
    # Get the order and create/retrieve invoice
    if order_type == 'appointment':
        order = get_object_or_404(Appointment, pk=order_id, patient=patient)
        amount = order.doctor.consultation_fee
        
        # Check for existing invoice
        invoice = Invoice.objects.filter(appointment=order, status=Invoice.Status.UNPAID).first()
        if not invoice:
            invoice = Invoice.objects.create(
                patient=patient,
                invoice_type=Invoice.InvoiceType.APPOINTMENT,
                appointment=order,
                amount=amount
            )
    
    elif order_type == 'pharmacy':
        order = get_object_or_404(PharmacyOrder, pk=order_id, patient=patient)
        amount = order.total_amount
        
        # Check for existing invoice
        invoice = Invoice.objects.filter(pharmacy_order=order, status=Invoice.Status.UNPAID).first()
        if not invoice:
            invoice = Invoice.objects.create(
                patient=patient,
                invoice_type=Invoice.InvoiceType.PHARMACY,
                pharmacy_order=order,
                amount=amount
            )
    else:
        messages.error(request, 'Invalid order type.')
        return redirect('patients:dashboard')
    
    # Create Razorpay order
    try:
        razorpay_order = razorpay_client.order.create({
            'amount': invoice.amount_in_paise,
            'currency': 'INR',
            'payment_capture': 1,
            'notes': {
                'invoice_id': invoice.pk,
                'order_type': order_type
            }
        })
        
        invoice.razorpay_order_id = razorpay_order['id']
        invoice.save()
        
    except Exception as e:
        messages.error(request, f'Error creating payment order: {str(e)}')
        return redirect('patients:dashboard')
    
    context = {
        'invoice': invoice,
        'order': order,
        'order_type': order_type,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': invoice.amount,
        'amount_in_paise': invoice.amount_in_paise,
        'user_email': request.user.email,
        'user_phone': request.user.phone or '',
        'user_name': request.user.get_full_name() or request.user.username,
    }
    return render(request, 'billing/payment.html', context)


@patient_required
def verify_payment(request):
    """Verify Razorpay payment after callback."""
    if request.method == 'POST':
        try:
            razorpay_order_id = request.POST.get('razorpay_order_id')
            razorpay_payment_id = request.POST.get('razorpay_payment_id')
            razorpay_signature = request.POST.get('razorpay_signature')
            
            # Verify signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            razorpay_client.utility.verify_payment_signature(params_dict)
            
            # Payment verified, update invoice
            invoice = get_object_or_404(Invoice, razorpay_order_id=razorpay_order_id)
            invoice.razorpay_payment_id = razorpay_payment_id
            invoice.razorpay_signature = razorpay_signature
            invoice.status = Invoice.Status.PAID
            invoice.paid_at = timezone.now()
            invoice.save()
            
            # Update related order status
            if invoice.invoice_type == Invoice.InvoiceType.APPOINTMENT:
                invoice.appointment.payment_status = 'paid'
                invoice.appointment.save()
            elif invoice.invoice_type == Invoice.InvoiceType.PHARMACY:
                invoice.pharmacy_order.status = 'paid'
                invoice.pharmacy_order.save()
            
            messages.success(request, 'Payment successful!')
            return redirect('billing:payment_success', invoice_id=invoice.pk)
            
        except razorpay.errors.SignatureVerificationError:
            messages.error(request, 'Payment verification failed.')
            return redirect('billing:payment_failure')
        except Exception as e:
            messages.error(request, f'Error processing payment: {str(e)}')
            return redirect('billing:payment_failure')
    
    return redirect('patients:dashboard')


@patient_required
def payment_success(request, invoice_id):
    """Payment success page."""
    patient = request.user.patient_profile
    invoice = get_object_or_404(Invoice, pk=invoice_id, patient=patient)
    
    context = {
        'invoice': invoice,
    }
    return render(request, 'billing/payment_success.html', context)


@patient_required
def payment_failure(request):
    """Payment failure page."""
    return render(request, 'billing/payment_failure.html')


@patient_required
def invoice_list(request):
    """List all invoices for patient."""
    patient = request.user.patient_profile
    invoices = Invoice.objects.filter(patient=patient).order_by('-created_at')
    
    context = {
        'invoices': invoices,
    }
    return render(request, 'billing/invoice_list.html', context)


@patient_required
def invoice_detail(request, pk):
    """View invoice details."""
    patient = request.user.patient_profile
    invoice = get_object_or_404(Invoice, pk=pk, patient=patient)
    
    context = {
        'invoice': invoice,
    }
    return render(request, 'billing/invoice_detail.html', context)


@csrf_exempt
def razorpay_webhook(request):
    """Handle Razorpay webhook notifications."""
    if request.method == 'POST':
        try:
            import json
            payload = json.loads(request.body)
            
            event = payload.get('event')
            
            if event == 'payment.captured':
                payment_entity = payload['payload']['payment']['entity']
                razorpay_order_id = payment_entity.get('order_id')
                razorpay_payment_id = payment_entity.get('id')
                
                # Update invoice
                try:
                    invoice = Invoice.objects.get(razorpay_order_id=razorpay_order_id)
                    if invoice.status != Invoice.Status.PAID:
                        invoice.razorpay_payment_id = razorpay_payment_id
                        invoice.status = Invoice.Status.PAID
                        invoice.paid_at = timezone.now()
                        invoice.save()
                        
                        # Update related order status
                        if invoice.invoice_type == Invoice.InvoiceType.APPOINTMENT:
                            invoice.appointment.payment_status = 'paid'
                            invoice.appointment.save()
                        elif invoice.invoice_type == Invoice.InvoiceType.PHARMACY:
                            invoice.pharmacy_order.status = 'paid'
                            invoice.pharmacy_order.save()
                except Invoice.DoesNotExist:
                    pass
            
            return HttpResponse(status=200)
        except Exception as e:
            return HttpResponse(status=400)
    
    return HttpResponse(status=405)
