from turtle import title
from django.test import TestCase
import pytest
from shop.forms import ProductDetailForm
from shop.models import Product, SizeOption, HandleOption, Category

@pytest.mark.django_db
def test_product_detail_form_valid():
    # Создаём категорию, так как у Product есть обязательное поле category
    category = Category.objects.create(title="Двери", slug="dveri")
    # Создаём товар
    product = Product.objects.create(
        name="Дверь 1",
        category=category,
        slug="dver-1",
        base_price=5000,
    )

    # Создаём размер (SizeOption)
    size_option = SizeOption.objects.create(product=product, size_name="2000*800", price_increase=500)

    # Создаём ручку (HandleOption)
    handle_option = HandleOption.objects.create(products=product, handle_name="алюминиевая", price_increase=300)

    # Данные для формы
    form_data = {
        "Размер": size_option.id,
        "Ручка": handle_option.id,
        "Порог": "да",
        "Открывание": "Левое (на себя, петли слева)",
        "Количество": 2,
    }

    # Создаём форму с данными и передаём продукт в `product`
    form = ProductDetailForm(data=form_data, product=product)

    # Проверяем, что форма валидна
    assert form.is_valid(), form.errors

@pytest.mark.django_db
def test_product_detail_form_invalid():
    # Создаём категорию, так как у Product есть обязательное поле category
    category = Category.objects.create(title="Двери", slug="dveri")

    # Создаём товар
    product = Product.objects.create(
        name="Дверь 2",
        category=category,
        slug="dver-2",
        base_price=5000,
    )

    # Создаём размер (SizeOption)
    size_option = SizeOption.objects.create(product=product, size_name="2000x800", price_increase=500)

    # Создаём ручку (HandleOption)
    handle_option = HandleOption.objects.create(products=product, handle_name="деревянная", price_increase=300)

    # Данные для формы с пропущенным обязательным полем "Размер"
    form_data = {
        # "Размер": size_option.id,  # Удалено, чтобы вызвать ошибку
        "Ручка": handle_option.id,
        "Порог": "да",
        "Открывание": "Левое (на себя, петли слева)",
        "Количество": 2,
    }

    # Создаём форму без обязательного поля
    form = ProductDetailForm(data=form_data, product=product)

    # Форма должна быть невалидной
    assert not form.is_valid(), "Форма не должна быть валидной без поля 'Размер'"

    # Проверяем, что в ошибках есть ключ "Размер"
    assert "Размер" in form.errors, f"Ожидалась ошибка по полю 'Размер', но получили: {form.errors}"

    