# products/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import gettext_lazy as _ # <--- ВОТ НЕОБХОДИМЫЙ ИМПОРТ
from django.http import HttpResponse

# Импортируем все наши модели и формы
from .models import Product, Order, OrderItem, Review
from .cart import Cart
from .forms import CartAddProductForm, OrderCreateForm, ReviewForm

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /cart/",
        "Disallow: /order/checkout/",
        "Disallow: /accounts/",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

# 1. Страница списка продуктов
def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})


# 2. Страница деталей продукта (с логикой отзывов)
def product_detail(request, pk):
    # prefetch_related('reviews__user') - оптимизация, чтобы загрузить все отзывы
    # и связанных с ними пользователей одним запросом, избегая "проблемы N+1".
    product = get_object_or_404(Product.objects.prefetch_related('reviews__user'), pk=pk)
    
    # Получаем все отзывы для данного продукта
    reviews = product.reviews.all()
    
    # Формы, которые будут на странице
    cart_product_form = CartAddProductForm()
    review_form = ReviewForm()
    
    # Переменная для проверки, оставлял ли уже пользователь отзыв
    user_has_reviewed = False
    
    # Проверяем, только если пользователь аутентифицирован
    if request.user.is_authenticated:
        if Review.objects.filter(product=product, user=request.user).exists():
            user_has_reviewed = True

    # Обработка POST-запроса, когда пользователь отправляет форму отзыва
    # 'submit_review' - это имя кнопки в форме отзыва, чтобы отличать ее от других форм
    if request.method == 'POST' and 'submit_review' in request.POST:
        # Убедимся, что пользователь залогинен, чтобы оставить отзыв
        if not request.user.is_authenticated:
            return redirect('login')

        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            # Проверяем еще раз, чтобы избежать дублирования отзывов
            if not user_has_reviewed:
                new_review = review_form.save(commit=False)
                new_review.product = product
                new_review.user = request.user
                new_review.save()
                messages.success(request, _('Спасибо за ваш отзыв!'))
                # Перенаправляем на ту же страницу, чтобы избежать повторной отправки формы
                return redirect(product.get_absolute_url())
            else:
                messages.error(request, _('Вы уже оставляли отзыв на этот товар.'))
    
    # Контекст, передаваемый в шаблон
    context = {
        'product': product,
        'cart_product_form': cart_product_form,
        'reviews': reviews,
        'review_form': review_form,
        'user_has_reviewed': user_has_reviewed,
        'contact_url': reverse('products:contact'),
        'login_url': reverse('login'), # Для ссылки "войдите, чтобы оставить отзыв"
    }
    return render(request, 'product_detail.html', context)


# 3. Добавление продукта в корзину
@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 quantity=cd['quantity'],
                 override_quantity=cd['override'])
    return redirect('products:cart_detail')


# 4. Удаление продукта из корзины
@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('products:cart_detail')


# 5. Страница деталей корзины
def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True
        })
    return render(request, 'cart_detail.html', {'cart': cart})


# 6. Страница оформления заказа
def order_checkout_page(request):
    cart = Cart(request)
    if not cart:
        return redirect('products:product_list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.paid = False
            order.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order, product=item['product'],
                    price=item['price'], quantity=item['quantity']
                )

            try:
                context = {'order': order}
                subject = render_to_string('email/order_created_email_subject.txt', context)
                subject = ''.join(subject.splitlines())
                html_message = render_to_string('email/order_created_email_body.html', context)
                send_mail(
                    subject, html_message, settings.DEFAULT_FROM_EMAIL,
                    settings.ORDER_NOTIFICATION_EMAILS, fail_silently=False,
                    html_message=html_message
                )
                print(f"Email уведомление о заказе №{order.id} успешно отправлено.")
            except Exception as e:
                print(f"Ошибка при отправке email уведомления для заказа №{order.id}: {e}")

            cart.clear()
            return render(request, 'order_created.html', {'order': order})
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email
            }
        form = OrderCreateForm(initial=initial_data)

    return render(request, 'order_checkout.html', {'cart': cart, 'form': form})


# 7. Страница подтверждения заказа
def order_created(request):
    return render(request, 'order_created.html', {})


# 8. Страница контактов
def contact_page(request):
    return render(request, 'contact.html')