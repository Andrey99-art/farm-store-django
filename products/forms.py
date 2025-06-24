# products/forms.py

from django import forms
from .models import Order, Review # Импортируем нужные модели
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

# --- Форма 1: Для добавления товара в корзину ---

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]

class CartAddProductForm(forms.Form):
    # Теперь это DecimalField, что позволяет вводить дробные числа
    quantity = forms.DecimalField(
        min_value=Decimal('0.05'), # Минимальное количество (например, 50г)
        max_value=100,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1' # Шаг для кнопок "вверх/вниз" в браузере
        }),
        label=_("Количество")
    )
    override = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput
    )

# --- Форма 2: Для оформления заказа ---

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone',
                  'address', 'postal_code', 'city']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': _('Ваше имя')}),
            'last_name': forms.TextInput(attrs={'placeholder': _('Ваша фамилия')}),
            'email': forms.EmailInput(attrs={'placeholder': _('Ваш email')}),
            'phone': forms.TextInput(attrs={'placeholder': '+7 (ХХХ) ХХХ-ХХ-ХХ'}),
            'address': forms.TextInput(attrs={'placeholder': _('Улица, дом, квартира')}),
            'postal_code': forms.TextInput(attrs={'placeholder': _('Индекс')}),
            'city': forms.TextInput(attrs={'placeholder': _('Город')}),
        }
        labels = {
            'first_name': _('Имя'),
            'last_name': _('Фамилия'),
            'email': _('Email'),
            'phone': _('Телефон'),
            'address': _('Адрес доставки'),
            'postal_code': _('Почтовый индекс'),
            'city': _('Город'),
        }

# --- Форма 3: Для добавления отзыва ---

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        # Указываем, какие поля из модели Review будут в форме
        fields = ['rating', 'text']
        
        # Настраиваем виджеты для полей
        widgets = {
            'rating': forms.NumberInput(attrs={
                'class': 'form-range', # Используем 'form-range' для красивого ползунка Bootstrap
                'type': 'range',       # Указываем тип 'range' для ползунка
                'min': 1, 
                'max': 5,
                'step': 1
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': _('Поделитесь вашими впечатлениями о продукте...')
            }),
        }
        
        # Настраиваем отображаемые названия полей
        labels = {
            'rating': _('Ваша оценка (от 1 до 5)'),
            'text': _('Ваш отзыв'),
        }