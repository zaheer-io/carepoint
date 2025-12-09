from django import forms
from .models import Medicine, PharmacyOrder


class MedicineForm(forms.ModelForm):
    """Form for creating/updating medicines."""
    
    class Meta:
        model = Medicine
        fields = [
            'name', 'generic_name', 'manufacturer', 'description',
            'price', 'stock', 'unit', 'prescription_required', 'image', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'generic_name': forms.TextInput(attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'prescription_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AddToCartForm(forms.Form):
    """Form for adding items to cart."""
    
    quantity = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 80px'})
    )


class CheckoutForm(forms.ModelForm):
    """Form for checkout."""
    
    class Meta:
        model = PharmacyOrder
        fields = ['shipping_address', 'notes']
        widgets = {
            'shipping_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
