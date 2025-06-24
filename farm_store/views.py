# farm_store/views.py

from django.shortcuts import redirect
from django.conf import settings

def set_language(request):
    """
    Устанавливает язык для текущей сессии пользователя на основе POST-запроса.
    """
    # Этот view теперь принимает только POST-запросы
    if request.method == 'POST':
        # Получаем язык и путь для возврата из данных формы
        language = request.POST.get('language')
        next_path = request.POST.get('next', '/') # По умолчанию возвращаемся на главную

        # Проверяем, что выбранный язык есть в списке доступных
        if language and language in [lang[0] for lang in settings.LANGUAGES]:
            # Собираем новый URL, добавляя языковой префикс к "чистому" пути
            # Например: /en + /cart/ = /en/cart/
            next_url = f"/{language}{next_path}"
            
            # Сохраняем выбор языка в сессии пользователя, используя стандартный ключ '_language'
            request.session['_language'] = language
            
            # Перенаправляем на новый URL
            return redirect(next_url)
    
    # Если что-то пошло не так (например, не POST-запрос),
    # возвращаемся на главную страницу без смены языка.
    return redirect('/')