from django.http import HttpRequest, HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Category, Product, CategoryImage, ProductImage, SizeOption, HandleOption, Favorite, Cart, Order, OrderItem
from .forms import ProductDetailForm
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages
from datetime import timedelta
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db import transaction
from django.forms.models import model_to_dict
from django_ratelimit.decorators import ratelimit
import re
from django.core.exceptions import ValidationError

def validate_order_form(data):
    errors = {}
    if not re.match(r'^[А-Яа-я]', data.get('first_name')):
        errors['first_name'] = 'Введите имя кириллицей!'
    if not re.match(r'^[А-Яа-я]', data.get('last_name')):
        errors['last_name'] = 'Введите фамилию кириллицей!'
    if not re.match(r'^((\+7|8)[-\s]?)?(\(?\d{3}\)?[-\s]?)?\d{3}[-\s]?\d{2}[-\s]?\d{2}$', data.get('phone', '')):
        errors['phone'] = 'Введите корректный номер телефона без пробелов!'
    if not data.get('email') or '@' not in data.get('email'):
        errors['email'] = 'Введите корректный email!'
    return errors


def catalog(request):
    parents = Category.objects.filter(parent=None).prefetch_related("images")  # Получить всех родителей
    family = {}
    for parent in parents:
        family[parent] = parent.get_children().prefetch_related("images") # Получить детей
    context = {
        "family": family,
    }
    return render(request, "shop/catalog.html", context=context)


def show_category(request: HttpRequest, category_slug: str) -> HttpResponse:
    # Получаем текущую категорию
    category = get_object_or_404(Category, slug=category_slug)
    ancestors = category.get_ancestors()
    parent_slug = ancestors.last().slug if ancestors else None

    # Получаем продукты данной категории и её потомков
    category_ids = category.get_descendants(include_self=True).values_list('id', flat=True)
    products = Product.objects.filter(category__id__in=category_ids, archived=False).order_by('-sales_sort', 'name')

    # Собираем доступные фильтры
    characteristics = {}
    for product in products:
        for key, value in product.characteristics.items():
            if key not in characteristics:
                characteristics[key] = set()
            characteristics[key].add(value)
    characteristics = {key: sorted(list(values)) for key, values in characteristics.items()}

    unique_sizes = (
        SizeOption.objects.filter(product__category__id__in=category_ids)
        .values_list('size_name', flat=True)
        .distinct()
        .order_by('size_name')
    )

    unique_handles = (
        HandleOption.objects.filter(products__category__id__in=category_ids)
        .values_list('handle_name', flat=True)
        .distinct()
        .order_by('handle_name')
    )

    # Применение фильтров
    filtered_products = products
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Получение данных фильтров из POST
        characteristics_filter = request.POST.getlist('characteristics')
        sizes_filter = request.POST.getlist('sizes')
        handles_filter = request.POST.getlist('handles')
        page = request.POST.get('page', 1)
    
        # print('Принятые фильтры:', {
        #     'characteristics': characteristics_filter,
        #     'sizes': sizes_filter,
        #     'handles': handles_filter,
        #     'page': page,
        # })

        # Применение фильтров
        if characteristics_filter:
            for char in characteristics_filter:
                try:
                    key, value = char.split(':', 1)  # Разделение ключа и значения
                    filtered_products = filtered_products.filter(**{f"characteristics__{key}": value})
                except ValueError:
                    print(f"Некорректный формат характеристики: {char}")
    
        if sizes_filter:
            filtered_products = filtered_products.filter(sizes__size_name__in=sizes_filter)
    
        if handles_filter:
            filtered_products = filtered_products.filter(handle_options__handle_name__in=handles_filter)


        # Собираем новые доступные фильтры после применения фильтров
        remaining_characteristics = {}
        for product in filtered_products:
            for key, value in product.characteristics.items():
                if key not in remaining_characteristics:
                    remaining_characteristics[key] = set()
                remaining_characteristics[key].add(value)
        remaining_characteristics = {key: sorted(list(values)) for key, values in remaining_characteristics.items()}
        
        remaining_sizes = list(
            SizeOption.objects.filter(product__in=filtered_products)
            .values_list('size_name', flat=True)
            .distinct()
        )
        
        remaining_handles = list(
            HandleOption.objects.filter(products__in=filtered_products)
            .values_list('handle_name', flat=True)
            .distinct()
        )
        
        # Пагинация
        paginator = Paginator(filtered_products.distinct(), 12)
        page_obj = paginator.get_page(page)
        
        # Генерация HTML для продуктов
        html = render_to_string('partials/product-list.html', {'products': page_obj})
        
        return JsonResponse({
            'html': html,
            'has_next': page_obj.has_next(),
            'characteristics': remaining_characteristics,
            'sizes': remaining_sizes,
            'handles': remaining_handles,
        })

    # Для обычного запроса (GET)
    page_number = request.GET.get('page', 1)
    paginator = Paginator(filtered_products, 12)
    page_obj = paginator.get_page(page_number)

    # Контекст для рендеринга страницы
    context = {
        'category': category,
        'products': page_obj,
        'has_next': page_obj.has_next(),
        'childrens': category.get_children().prefetch_related("images"),
        'ancestors': ancestors,
        'parent_slug': parent_slug,
        'characteristics': characteristics,
        'unique_sizes': unique_sizes,
        'unique_handles': unique_handles
    }
    return render(request, 'shop/category_product_list.html', context=context)




def view_product(request: HttpRequest, product_slug : str) -> HttpResponse:

    product = get_object_or_404(Product, slug=product_slug)
    ancestors = product.category.get_ancestors().prefetch_related("images")
    if 'Престиж' in product.name:
        threshold_price_inc = 0
    else:
        threshold_price_inc = 1500
        
    if request.method == 'POST':
        form = ProductDetailForm(request.POST, product=product)
        if form.is_valid():
            size_option = form.cleaned_data['Размер']
            handle_option = form.cleaned_data['Ручка']
            threshold = form.cleaned_data['Порог']
            opening_side = form.cleaned_data['Открывание']
            quantity = form.cleaned_data['Количество']

            # Рассчитываем итоговую цену
            threshold_price = threshold_price_inc if threshold == 'да' else 0
            base_price = product.base_price + size_option.price_increase + handle_option.price_increase + threshold_price

            action = request.POST.get('action')

            # Добавление в избранное (для всех пользователей)
            if action == 'add_to_favorites':
                session_key = request.session.session_key
                if not session_key:
                    request.session.create()
                    session_key = request.session.session_key
                # Парсинг размеров из size_option
                size_parts = size_option.size_name.split('*')
                height, width = map(int, size_parts)
                if 'Престиж' in product.name:
                    box_height = height - 10
                    box_width = width - 10
                    if 'с порогом' in product.name:
                        glass_height = height - 130
                    else:
                        glass_height = height - 75
                    glass_width = width - 100
                    air_gap = '15-20мм' if threshold == 'да' else '20мм'
                else:
                    box_height = height if threshold == 'да' else height - 10
                    box_width = width - 10
                    glass_height = height - 65
                    glass_width = width - 80
                    air_gap = '18мм' if threshold == 'да' else '20мм'

                Favorite.objects.get_or_create(
                    user=request.user if request.user.is_authenticated else None,
                    session_key=session_key if not request.user.is_authenticated else None,
                    product=product,
                    size_option=size_option,
                    handle_option=handle_option,
                    threshold=threshold,
                    opening_side=opening_side,
                    price=base_price,
                    box_size=f"{box_height}*{box_width}",
                    glass_size=f"{glass_height}*{glass_width}",
                    air_gap=air_gap
                )
                messages.success(request, "Товар добавлен в избранное!")
                return redirect('shop:product-view', product_slug=product_slug)

            # Добавление в корзину (с количеством)
            elif action == 'add_to_cart':
                session_key = request.session.session_key or request.session.create()
                Cart.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    session_key=session_key if not request.user.is_authenticated else None,
                    product=product,
                    size_option=size_option,
                    handle_option=handle_option,
                    threshold=threshold,
                    opening_side=opening_side,
                    quantity=quantity,
                    price=base_price
                )
                messages.success(request, "Товар добавлен в корзину!")
                return redirect('shop:product-view', product_slug=product_slug)
            else:
                messages.error(request, "Пожалуйста, заполните форму корректно.")
        else:
            print("Ошибки формы:", form.errors)  # Печатаем ошибки валидации формы
    else:
        # Создаем пустую форму с переданным продуктом
        form = ProductDetailForm(product=product)

    context = {
        "product": product,
        'ancestors':ancestors,
        'form': form,
        'threshold_price_inc': threshold_price_inc,
    }
    return render(request, 'shop/product_view.html', context=context)


def custom_logout(request):
    if not request.user.is_anonymous:
        # Сохраняем session_key в old_session_key перед разлогином
        session_key = request.session.session_key
        if session_key:
            request.session['old_session_key'] = session_key
    logout(request)  # Выполняем стандартный разлогин
    return redirect('shop:catalog')  # Перенаправление после разлогина


def favorites_view(request):
    # Получаем или создаем session_key
    session_key = request.session.session_key or request.session.create()
    
    # Избранное для авторизованных и анонимных
    if request.user.is_authenticated:
        favorite_items = Favorite.objects.filter(user=request.user)
    else:
        favorite_items = Favorite.objects.filter(session_key=session_key)

    # print("[VIEW] Количество товаров в избранном:", len(favorite_items))

    if request.method == "POST":
        action = request.POST.get('action')
        favorite_id = request.POST.get('favorite_id')
        # print("[POST] Действие:", action, "favorite_id:", favorite_id)

        if request.user.is_authenticated:
            favorite_item = get_object_or_404(Favorite, id=favorite_id, user=request.user)
        else:
            favorite_item = get_object_or_404(Favorite, id=favorite_id, session_key=session_key)

        if action == "add_to_cart":
            quantity = int(request.POST.get('quantity', 1))
            # print("[POST] Добавление в корзину, количество:", quantity)

            Cart.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=session_key if not request.user.is_authenticated else None,
                product=favorite_item.product,
                size_option=favorite_item.size_option,
                handle_option=favorite_item.handle_option,
                threshold=favorite_item.threshold,
                opening_side=favorite_item.opening_side,
                quantity=quantity,
                price=favorite_item.price,
            )
            messages.success(request, "Товар добавлен в корзину!")
            return redirect('shop:favorites')

        elif action == "remove":
            # print("[POST] Удаление из избранного")
            favorite_item.delete()
            messages.success(request, "Товар удален из избранного!")
            return redirect('shop:favorites')

    return render(request, 'shop/favorites.html', {'favorite_items': favorite_items})


def cart_view(request):
    # Получаем или создаем session_key
    session_key = request.session.session_key or request.session.create()
    
#    # Предзаполнение формы, если пользователь аутентифицирован
#    initial_data = {}
#    # корзина для авторизованных и анонимных
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
#        initial_data = {
#            'last_name': request.user.last_name,
#            'first_name': request.user.first_name,
#            'phone': request.user.profile.phone_number if hasattr(request.user, 'profile') else '',
#            'email': request.user.email,
#            'address': request.user.profile.city if hasattr(request.user, 'profile') else ''
#        }
    else:
        cart_items = Cart.objects.filter(session_key=session_key)

    # print("[VIEW] Количество товаров в корзине:", len(cart_items))
         #Если пользователь зарегистрирован, предварительно заполняем данные
    
    if request.method == "POST":
        action = request.POST.get('action')
        # print("[POST] Действие:", action)

        if action == "update" or action == "remove":
            cart_id = request.POST.get('cart_id')
            # print("[POST] Действие:", action, "cart_id:", cart_id)

            if request.user.is_authenticated:
                cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
            else:
                cart_item = get_object_or_404(Cart, id=cart_id, session_key=session_key)

            if action == "update":
                # Обновить количество
                quantity = int(request.POST.get('quantity', 1))
                if quantity > 0:
                    cart_item.quantity = quantity
                    cart_item.save()
                    messages.success(request, "Количество обновлено!")
                else:
                    cart_item.delete()
                    messages.success(request, "Товар удален из корзины!")
                return redirect('shop:cart')

            elif action == "remove":
                # Удалить товар из корзины
                cart_item.delete()
                messages.success(request, "Товар удален из корзины!")
                return redirect('shop:cart')

#        elif action == "checkout":
#            # Обработка формы заказа
#            last_name = request.POST.get('last_name')
#            first_name = request.POST.get('first_name')
#            phone = request.POST.get('phone')
#            email = request.POST.get('email')
#            address = request.POST.get('address')
#            delivery_method = request.POST.get('delivery_method')
#            custom_delivery = request.POST.get('custom_delivery')
#            payment_method = request.POST.get('payment_method')
#            total_price=sum(item.price for item in cart_items)
#            print("[POST] Данные формы:",
#                  last_name, first_name, phone, email, address, delivery_method, payment_method, total_price)
#
#            if not cart_items.exists():
#                messages.error(request, "Корзина пуста! Невозможно создать заказ.")
#                return redirect('shop:cart')
#
#            try:
#                with transaction.atomic():
#                    # Создание заказа
#                    order = Order.objects.create(
#                        user=request.user if request.user.is_authenticated else None,
#                        session_key=session_key if not request.user.is_authenticated else None,
#                        last_name=last_name,
#                        first_name=first_name,
#                        phone=phone,
#                        email=email,
#                        address=address,
#                        delivery_method=delivery_method,
#                        custom_delivery=custom_delivery,
#                        payment_method=payment_method,
#                        total_price=total_price,
#                        status="В обработке"  # Устанавливаем начальный статус
#                    )
#                    print("[ORDER] Создан заказ:", order)
#
#                    # Перенос товаров из корзины в заказ
#                    for cart_item in cart_items:
#                        print("[ORDER ITEM] Перенос товара в заказ:", cart_item)
#                        OrderItem.objects.create(
#                            order=order,
#                            product=cart_item.product,
#                            size_option=cart_item.size_option,
#                            opening_side=cart_item.opening_side,
#                            threshold=cart_item.threshold,
#                            handle_option=cart_item.handle_option,
#                            price=cart_item.price,
#                            quantity=cart_item.quantity
#                        )
#
#                    # Очистка корзины
#                    cart_items.delete()
#                    print("[CART] Корзина очищена")
#
#                messages.success(request, "Заказ успешно создан!")
#                return redirect('shop:cart')
#                #return redirect('shop:order_detail', order_id=order.id)
#
#            except Exception as e:
#                print("[ERROR] Ошибка при создании заказа:", str(e))
#                messages.error(request, "Произошла ошибка при создании заказа. Попробуйте еще раз.")
#                return redirect('shop:cart')

    return render(request, 'shop/cart.html', {'cart_items': cart_items})


def order_view(request):
    # Получаем или создаем session_key
    session_key = request.session.session_key or request.session.create()
    
    # Предзаполнение формы, если пользователь аутентифицирован
    initial_data = {}
    # корзина для авторизованных и анонимных
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        initial_data = {
            'last_name': request.user.last_name,
            'first_name': request.user.first_name,
            'phone': request.user.profile.phone_number if hasattr(request.user, 'profile') else '',
            'email': request.user.email,
            'address': request.user.profile.city if hasattr(request.user, 'profile') else ''
        }
    else:
        cart_items = Cart.objects.filter(session_key=session_key)

    # print("[VIEW] Количество товаров в корзине:", len(cart_items))
         #Если пользователь зарегистрирован, предварительно заполняем данные
    
    if request.method == "POST":

        errors = validate_order_form(request.POST)
        if errors:
            for field, error in errors.items():
                messages.error(request, f"{field.capitalize()}: {error}")
            return render(request, 'shop/order.html', {'cart_items': cart_items, 'initial_data': request.POST})
        
        action = request.POST.get('action')
        # print("[POST] Действие:", action)

        if action == "checkout":
            # Обработка формы заказа
            last_name = request.POST.get('last_name')
            first_name = request.POST.get('first_name')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            address = request.POST.get('address')
            delivery_method = request.POST.get('delivery_method')
            custom_delivery = request.POST.get('custom_delivery')
            payment_method = request.POST.get('payment_method')
            total_price=sum(item.price*item.quantity for item in cart_items)
            # print("[POST] Данные формы:",
            #       last_name, first_name, phone, email, address, delivery_method, payment_method, total_price)

            if not cart_items.exists():
                messages.error(request, "Корзина пуста! Невозможно создать заказ.")
                return redirect('shop:cart')

            try:
                with transaction.atomic():
                    # Создание заказа
                    order = Order.objects.create(
                        user=request.user if request.user.is_authenticated else None,
                        session_key=session_key if not request.user.is_authenticated else None,
                        last_name=last_name,
                        first_name=first_name,
                        phone=phone,
                        email=email,
                        address=address,
                        delivery_method=delivery_method,
                        custom_delivery=custom_delivery,
                        payment_method=payment_method,
                        total_price=total_price,
                        status="В обработке"  # Устанавливаем начальный статус
                    )
                    # print("[ORDER] Создан заказ:", order)

                    # Перенос товаров из корзины в заказ
                    for cart_item in cart_items:
                        # print("[ORDER ITEM] Перенос товара в заказ:", cart_item)
                        OrderItem.objects.create(
                            order=order,
                            product=cart_item.product,
                            size_option=cart_item.size_option,
                            opening_side=cart_item.opening_side,
                            threshold=cart_item.threshold,
                            handle_option=cart_item.handle_option,
                            price=cart_item.price,
                            quantity=cart_item.quantity
                        )

                    # Очистка корзины
                    cart_items.delete()
                    # print("[CART] Корзина очищена")

                messages.success(request, "Заказ успешно создан!")
                return redirect('shop:cart')
                #return redirect('shop:order_detail', order_id=order.id)

            except Exception as e:
                # print("[ERROR] Ошибка при создании заказа:", str(e))
                messages.error(request, "Произошла ошибка при создании заказа. Попробуйте еще раз.")
                return redirect('shop:cart')

    return render(request, 'shop/order.html', {'cart_items': cart_items, 'initial_data': initial_data})




