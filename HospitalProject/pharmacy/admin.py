from django.contrib import admin
from .models import Medicine, PharmacyOrder, OrderItem, Cart, CartItem

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'generic_name', 'price', 'stock', 'unit', 'is_active')
    list_filter = ('is_active', 'prescription_required')
    search_fields = ('name', 'generic_name', 'manufacturer')
    list_editable = ('price', 'stock', 'is_active')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(PharmacyOrder)
class PharmacyOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('patient__user__username', 'id')
    inlines = [OrderItemInline]
    list_editable = ('status',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('patient', 'updated_at')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'medicine', 'quantity', 'subtotal')
