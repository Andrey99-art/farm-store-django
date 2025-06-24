# products/cart.py

from decimal import Decimal
from django.conf import settings
from products.models import Product

class Cart:
    def __init__(self, request):
        """
        Инициализация корзины.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Сохраняем пустую корзину в сессии
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Добавить продукт в корзину или обновить его количество.
        """
        product_id = str(product.id) # Ключи словарей в сессии должны быть строками

        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)} # Цена хранится как строка для совместимости с JSON

        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        """
        Пометить сессию как "измененную", чтобы она сохранилась.
        """
        self.session.modified = True

    def remove(self, product):
        """
        Удалить продукт из корзины.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Перебор элементов в корзине и получение продуктов из базы данных.
        """
        product_ids = self.cart.keys()
        # получаем объекты Product и добавляем их в корзину
        products = Product.objects.filter(id__in=product_ids)

        cart = self.cart.copy() # Создаем копию, чтобы не менять итерируемый объект
        for product in products:
            cart[str(product.id)]['product'] = product # Добавляем объект Product в каждый элемент корзины

        for item in cart.values():
            # Конвертируем цену обратно в Decimal
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item # yield делает итератор

    def __len__(self):
        """
        Подсчет всех элементов в корзине.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Подсчет общей стоимости товаров в корзине.
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """
        Очистить корзину из сессии.
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()