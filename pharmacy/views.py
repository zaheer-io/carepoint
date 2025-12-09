from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from accounts.decorators import patient_required
from .models import Medicine, Cart, CartItem, PharmacyOrder, OrderItem
from .forms import AddToCartForm, CheckoutForm


def medicine_list(request):
    """List all available medicines."""
    medicines = Medicine.objects.filter(is_active=True, stock__gt=0)
    
    search = request.GET.get('search', '')
    if search:
        medicines = medicines.filter(name__icontains=search)
    
    context = {
        'medicines': medicines,
        'search': search,
    }
    return render(request, 'pharmacy/medicine_list.html', context)


def medicine_detail(request, pk):
    """View medicine details."""
    medicine = get_object_or_404(Medicine, pk=pk, is_active=True)
    
    context = {
        'medicine': medicine,
        'add_form': AddToCartForm(),
    }
    return render(request, 'pharmacy/medicine_detail.html', context)


@patient_required
def add_to_cart(request, pk):
    """Add medicine to cart."""
    medicine = get_object_or_404(Medicine, pk=pk, is_active=True)
    patient = request.user.patient_profile
    
    # Get or create cart
    cart, _ = Cart.objects.get_or_create(patient=patient)
    
    if request.method == 'POST':
        form = AddToCartForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            
            # Check stock
            if quantity > medicine.stock:
                messages.error(request, 'Not enough stock available.')
                return redirect('pharmacy:medicine_detail', pk=pk)
            
            # Add or update cart item
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                medicine=medicine,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            messages.success(request, f'{medicine.name} added to cart!')
            return redirect('pharmacy:view_cart')
    
    return redirect('pharmacy:medicine_detail', pk=pk)


@patient_required
def view_cart(request):
    """View shopping cart."""
    patient = request.user.patient_profile
    cart, _ = Cart.objects.get_or_create(patient=patient)
    
    context = {
        'cart': cart,
    }
    return render(request, 'pharmacy/cart.html', context)


@patient_required
def update_cart_item(request, pk):
    """Update cart item quantity."""
    patient = request.user.patient_profile
    cart_item = get_object_or_404(CartItem, pk=pk, cart__patient=patient)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0 and quantity <= cart_item.medicine.stock:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated.')
        else:
            messages.error(request, 'Invalid quantity.')
    
    return redirect('pharmacy:view_cart')


@patient_required
def remove_from_cart(request, pk):
    """Remove item from cart."""
    patient = request.user.patient_profile
    cart_item = get_object_or_404(CartItem, pk=pk, cart__patient=patient)
    
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    
    return redirect('pharmacy:view_cart')


@patient_required
def checkout(request):
    """Checkout and create order."""
    patient = request.user.patient_profile
    cart = get_object_or_404(Cart, patient=patient)
    
    if cart.item_count == 0:
        messages.error(request, 'Your cart is empty.')
        return redirect('pharmacy:view_cart')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order
            order = PharmacyOrder.objects.create(
                patient=patient,
                shipping_address=form.cleaned_data['shipping_address'],
                notes=form.cleaned_data['notes']
            )
            
            # Move cart items to order
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    medicine=cart_item.medicine,
                    quantity=cart_item.quantity,
                    price=cart_item.medicine.price
                )
            
            # Calculate total
            order.calculate_total()
            order.save()
            
            # Clear cart
            cart.items.all().delete()
            
            messages.success(request, 'Order placed successfully!')
            return redirect('billing:payment', order_type='pharmacy', order_id=order.pk)
    else:
        form = CheckoutForm(initial={'shipping_address': patient.address})
    
    context = {
        'cart': cart,
        'form': form,
    }
    return render(request, 'pharmacy/checkout.html', context)


@patient_required
def order_history(request):
    """View order history."""
    patient = request.user.patient_profile
    orders = PharmacyOrder.objects.filter(patient=patient).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'pharmacy/order_history.html', context)


@patient_required
def order_detail(request, pk):
    """View order details."""
    patient = request.user.patient_profile
    order = get_object_or_404(PharmacyOrder, pk=pk, patient=patient)
    
    context = {
        'order': order,
    }
    return render(request, 'pharmacy/order_detail.html', context)
