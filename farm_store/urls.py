# farm_store/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings # <-- Проверьте этот импорт
from django.conf.urls.static import static # <-- Проверьте этот импорт
from django.conf.urls.i18n import i18n_patterns
from django.contrib.sitemaps.views import sitemap
from products.sitemaps import ProductSitemap

from . import views as project_views
from products.views import robots_txt

sitemaps = {
    'products': ProductSitemap,
}

# URL-адреса без языкового префикса
urlpatterns = [
    path('admin/', admin.site.urls),
    path('set-language/', project_views.set_language, name='set_language'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt),
]

# URL-адреса с языковым префиксом
urlpatterns += i18n_patterns(
    path('', include('products.urls')),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
)

# --- ДОБАВЬТЕ ЭТОТ БЛОК, ЕСЛИ ЕГО НЕТ ---
if settings.DEBUG:
    # Добавляем маршруты для медиа-файлов (загруженные пользователем изображения)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Добавляем маршруты для статических файлов (CSS, JS, favicon.ico)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)