# products/admin.py

from django.contrib import admin
from .models import Product, Order, OrderItem, Review

# Импорт для работы с переводимыми моделями в админ-панели
from parler.admin import TranslatableAdmin


# --- 1. Настройки для модели Заказа (Order) ---

class OrderItemInline(admin.TabularInline):
    """
    Позволяет отображать и редактировать позиции заказа (OrderItem)
    прямо на странице самого заказа (Order).
    """
    model = OrderItem
    # raw_id_fields удобен при большом количестве продуктов,
    # чтобы не загружать огромный выпадающий список.
    raw_id_fields = ['product']
    fields = ['product', 'price', 'quantity']
    # extra = 0 убирает пустые "слоты" для добавления новых позиций по умолчанию.
    extra = 0
    # Делаем поля только для чтения, так как заказ не должен меняться после создания
    readonly_fields = ['product', 'price', 'quantity']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Настройки отображения модели Order в админ-панели.
    """
    list_display = [
        'id', 'first_name', 'last_name', 'email',
        'paid', 'created'
    ]
    list_filter = ['paid', 'created', 'updated']
    search_fields = ['id', 'first_name', 'last_name', 'email']
    inlines = [OrderItemInline]


# --- 2. Настройки для модели Продукта (Product) ---

@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    list_display = ('name', 'price', 'unit', 'created_at') # <-- Добавляем 'unit'
    list_filter = ('created_at', 'unit') # <-- Добавляем 'unit' в фильтры


# --- 3. Настройки для модели Отзыва (Review) ---

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Настройки отображения модели Review для модерации отзывов.
    """
    # Поля, которые будут отображаться в списке всех отзывов.
    list_display = ('product', 'user', 'rating', 'created_at')
    
    # Позволяет фильтровать отзывы по рейтингу и дате.
    list_filter = ('rating', 'created_at')
    
    # Позволяет искать отзывы по имени пользователя, названию продукта или тексту.
    search_fields = ('user__username', 'product__translations__name', 'text')
    
    # Делаем поля только для чтения, так как отзывы не должны редактироваться администратором
    readonly_fields = ('product', 'user', 'rating', 'text', 'created_at')