from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Category, Product, CategoryImage, ProductImage, SizeOption
from .forms import ProductDetailForm

def catalog(request):
    parents = Category.objects.filter(parent=None).prefetch_related("images")  # Получить всех родителей
    family = {}
    for parent in parents:
        family[parent] = parent.get_children().prefetch_related("images") # Получить детей
    context = {
        "family": family,
    }
    return render(request, "shop/catalog.html", context=context)


def show_category(request: HttpRequest, category_slug : str) -> HttpResponse:
    category = Category.objects.get(slug=category_slug)
    products = {}
    product = Product.objects.filter(category=category)
    # записываем словарь продуктами категории в которой находимся
    if product:
        for obj in product:
            products[(obj.sales_sort, obj.name)] = obj
    # записываем словарь продуктами категорий потомков
    for cat in category.get_descendants():
        product = Product.objects.filter(category=cat)
        if product:
            for obj in product:
                products[(obj.sales_sort, obj.name)] = obj
    # Создаем дублирующий словарь для хранения отсортированных значений
    sorted_products = {}
    # Сортируем значения по убыванию числового значения в ключе
    sorted_values = sorted(products.items(), key=lambda x: int(x[0][0]), reverse=True)
    # Добавляем пары ключ-значение из отсортированного списка в новый словарь
    for key, value in sorted_values:
        sorted_products[key] = value
    context = {
        'category': category,
        "products": sorted_products,
        'childrens': category.get_children().prefetch_related("images"),
        'ancestors': category.get_ancestors(),
        }
    return render(request, 'shop/category_product_list.html', context=context)

def view_product(request: HttpRequest, product_slug : str) -> HttpResponse:
    product = get_object_or_404(Product, slug=product_slug)
    ancestors = product.category.get_ancestors().prefetch_related("images")
    if request.method == 'POST':
        form = ProductDetailForm(request.POST, product=product)
        if form.is_valid():
            # Обработка формы, например, создание заказа
            size_option = form.cleaned_data['size_option']
            handle_option = form.cleaned_data['handle_option']
            # Рассчитываем итоговую цену (пример)
            final_price = product.base_price + size_option.price_increase + handle_option.price_increase
            # Здесь вы можете сделать что-то с выбранным размером (например, добавить в корзину)
            # Пример:
            # order = Order.objects.create(product=product, size=size_option)
            #return render(request, 'order_confirmation.html', {'size_option': size_option, 'product': product})
    else:
        # Создаем пустую форму с переданным продуктом
        form = ProductDetailForm(product=product)

    context = {
        "product": product,
        'ancestors':ancestors,
        'form': form,
    }
    return render(request, 'shop/product_view.html', context=context)


class Product_Datails(DetailView):
    template_name = 'shop/product_view.html'
    queryset = Product.objects.select_related('sizes')
    context_object_name = 'product'
