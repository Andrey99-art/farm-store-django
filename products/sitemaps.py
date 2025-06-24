# products/sitemaps.py

from django.contrib.sitemaps import Sitemap
from .models import Product

class ProductSitemap(Sitemap):
    changefreq = "weekly"  # Как часто страницы могут меняться
    priority = 0.9         # Приоритет страницы (от 0.0 до 1.0)

    def items(self):
        # Возвращает все объекты, которые должны быть в карте сайта
        return Product.objects.all()

    def lastmod(self, obj):
        # Возвращает дату последнего изменения объекта
        # (предполагая, что у вас есть поле `updated_at` или `created_at`)
        return obj.created_at