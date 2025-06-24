# products/models.py

from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Avg

# Импорты для django-parler
from parler.models import TranslatableModel, TranslatedFields


# --- 1. Модель Продукта ---

class Product(TranslatableModel):
    """
    Модель продукта с поддержкой многоязычности.
    """
    # Непереводимые поля
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_("Цена (по желанию)")
    )
    image = models.ImageField(
        upload_to='product_images/',
        verbose_name=_("Изображение продукта")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата добавления")
    )

    # Переводимые поля
    translations = TranslatedFields(
        name=models.CharField(max_length=200, verbose_name=_("Название продукта")),
        description=models.TextField(verbose_name=_("Описание"))
    )

    class Units(models.TextChoices):
        KILOGRAM = 'kg', _('кг')
        GRAM = 'g', _('г')
        PIECE = 'pc', _('шт.')
        LITER = 'l', _('л')

    unit = models.CharField(
        max_length=2,
        choices=Units.choices,
        default=Units.PIECE,
        verbose_name=_("Единица измерения")
    )

    class Meta:
        verbose_name = _("Продукт")
        verbose_name_plural = _("Продукты")
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:product_detail', args=[self.id])

    def average_rating(self):
        """
        Рассчитывает и возвращает средний рейтинг продукта на основе всех отзывов.
        Возвращает 0, если отзывов нет.
        """
        # self.reviews - это related_name из модели Review
        avg = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0


# --- 2. Модель Заказа ---

class Order(models.Model):
    """
    Модель заказа, хранящая информацию о клиенте и деталях заказа.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Пользователь")
    )
    first_name = models.CharField(max_length=50, verbose_name=_("Имя"))
    last_name = models.CharField(max_length=50, verbose_name=_("Фамилия"))
    email = models.EmailField(verbose_name=_("Email"))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_("Телефон (по желанию)"))
    address = models.CharField(max_length=250, verbose_name=_("Адрес доставки"))
    postal_code = models.CharField(max_length=20, verbose_name=_("Почтовый индекс"))
    city = models.CharField(max_length=100, verbose_name=_("Город"))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))
    paid = models.BooleanField(default=False, verbose_name=_("Оплачен"))

    class Meta:
        ordering = ('-created',)
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")

    def __str__(self):
        return f'{_("Order")} №{self.id}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


# --- 3. Модель Позиции в Заказе ---

class OrderItem(models.Model):
    """
    Модель, представляющая один товар внутри заказа.
    """
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name=_("Заказ"))
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE, verbose_name=_("Продукт"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Цена за ед."))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Количество"))

    class Meta:
        verbose_name = _("Позиция заказа")
        verbose_name_plural = _("Позиции заказа")

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity


# --- 4. Модель Отзыва ---

class Review(models.Model):
    """
    Модель для хранения отзывов и рейтингов от пользователей к продуктам.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews', # Позволяет обращаться к отзывам через product.reviews.all()
        verbose_name=_("Продукт")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Пользователь")
    )
    rating = models.IntegerField(
        default=5,
        validators=[MaxValueValidator(5), MinValueValidator(1)],
        verbose_name=_("Рейтинг (от 1 до 5)")
    )
    text = models.TextField(
        max_length=2000,
        verbose_name=_("Текст отзыва")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания")
    )

    class Meta:
        verbose_name = _("Отзыв")
        verbose_name_plural = _("Отзывы")
        ordering = ['-created_at']
        # Гарантирует, что один пользователь может оставить только один отзыв на один продукт
        unique_together = ('product', 'user')

    def __str__(self):
        return f'{_("Review by")} {self.user.username} {_("for")} {self.product.name}'