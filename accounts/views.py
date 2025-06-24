# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login # Импортируем функцию login
from django.contrib.auth.forms import UserCreationForm # Используем готовую форму Django
from django.contrib.auth.decorators import login_required 
from products.models import Order
from django.urls import reverse


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() # Сохраняем нового пользователя в БД
            login(request, user) # Автоматически входим под созданным пользователем
            return redirect('products:product_list') # Перенаправляем на главную страницу
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required # Этот декоратор гарантирует, что только залогиненные пользователи могут видеть эту страницу
def my_orders(request):
    # Получаем все заказы, которые связаны с текущим пользователем
    # и сортируем их от новых к старым.
    # Prefetch_related('items__product') - это оптимизация. Она загружает все связанные
    # OrderItem и их продукты одним запросом, предотвращая множество запросов к БД в цикле.
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created')
    return render(request, 'registration/my_orders.html', {
        'orders': orders,
        'product_list_url': reverse('products:product_list')
    })