from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from .models import Category, Product, CategoryImage, ProductImage

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
    print(sorted_values)
    for key, value in sorted_values:
        sorted_products[key] = value
    context = {
        'category': category,
        "products": sorted_products,
        'childrens': category.get_children(),
        'ancestors': category.get_ancestors(),
        }
    return render(request, 'shop/category_product_list.html', context=context)

def show_product(request: HttpRequest, product_slug : str) -> HttpResponse:
    product = get_object_or_404(Product, slug=product_slug)
    ancestors = product.category.get_ancestors()
    context = {
        "product": product,
        'ancestors':ancestors,
    }

    return render(request, 'shop/product_view.html', context=context)