# products/urls.py

from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('contact/', views.contact_page, name='contact'),

    # URL'ы для корзины
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/', views.cart_detail, name='cart_detail'),

    # URL'ы для оформления заказа
    path('order/checkout/', views.order_checkout_page, name='order_checkout'),
    path('order/created/', views.order_created, name='order_created'), # Новый URL
]