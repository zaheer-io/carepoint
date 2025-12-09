from django.urls import path
from . import views

app_name = 'pharmacy'

urlpatterns = [
    path('medicines/', views.medicine_list, name='medicine_list'),
    path('medicines/<int:pk>/', views.medicine_detail, name='medicine_detail'),
    path('medicines/<int:pk>/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/item/<int:pk>/update/', views.update_cart_item, name='update_cart_item'),
    path('cart/item/<int:pk>/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
]
