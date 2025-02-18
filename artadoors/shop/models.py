from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.timezone import now
from datetime import timedelta


class Product(models.Model):
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name',]

    name = models.CharField(max_length=100)
    category = TreeForeignKey('Category', on_delete=models.PROTECT, related_name='products', verbose_name='Категория')
    slug = models.SlugField(max_length=255, verbose_name="URL")
    description = models.TextField(null=True, blank=True, verbose_name='Индивидуальное описание товара')
    archived = models.BooleanField(default=False)
    base_price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Начальная цена")  # базовая цена
    characteristics = models.JSONField(null=True, blank=True, verbose_name='Характеристики в формате JSON')  # характеристики
    sales_sort = models.IntegerField(null=True, blank=True, verbose_name='Порядок сортировки')

    def __str__(self):
        return self.name


class SizeOption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')
    size_name = models.CharField(max_length=10)  # название размера
    price_increase = models.DecimalField(max_digits=5, decimal_places=0)  # увеличение цены за размер

    def __str__(self):
        return self.size_name  # Возвращаем название размера при отображении объекта


class HandleOption(models.Model):
    products = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='handle_options')
    handle_name = models.CharField(max_length=100)  # название
    price_increase = models.DecimalField(max_digits=5, decimal_places=0)    # увеличение цены за опцию

    def __str__(self):
        return self.handle_name


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    size_option = models.ForeignKey('SizeOption', on_delete=models.CASCADE)
    handle_option = models.ForeignKey('HandleOption', on_delete=models.CASCADE)
    threshold = models.CharField(max_length=3, choices=[('да', 'Да'), ('нет', 'Нет')])
    opening_side = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    added_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        unique_together = ['session_key', 'product', 'size_option', 'handle_option', 'threshold', 'opening_side']

    @property
    def total_price(self):
        """Общая стоимость позиции в корзине."""
        return self.quantity * self.price
    

    def __str__(self):
        return f"{self.product.name} ({self.user or self.session_key})"
    
    @staticmethod
    def clean_old_sessions():
        """Удаляет корзину с истекшими сессиями (старше 7 дней)"""
        expiration_date = now() - timedelta(days=7)
        Cart.objects.filter(user__isnull=True, added_at__lt=expiration_date).delete()
    

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    size_option = models.ForeignKey('SizeOption', on_delete=models.CASCADE)
    handle_option = models.ForeignKey('HandleOption', on_delete=models.CASCADE)
    threshold = models.CharField(max_length=100, null=True, blank=True)
    opening_side = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    added_at = models.DateTimeField(auto_now_add=True, null=True)
    box_size = models.CharField(max_length=100, null=True, blank=True)  # Размер коробки
    glass_size = models.CharField(max_length=100, null=True, blank=True)  # Размер стекла
    air_gap = models.CharField(max_length=100, null=True, blank=True)  # Приточка воздуха

    class Meta:
        unique_together = ['session_key', 'product', 'size_option', 'handle_option', 'threshold', 'opening_side']

    def __str__(self):
        return f"{self.product.name} ({self.user or self.session_key})"
    
    @staticmethod
    def clean_old_sessions():
        """Удаляет избранное с истекшими сессиями (старше 7 дней)"""
        expiration_date = now() - timedelta(days=7)
        Favorite.objects.filter(user__isnull=True, added_at__lt=expiration_date).delete()

def product_images_dir(instance, filename):
    return 'imgs/product_{slug}/{filename}'.format(slug=instance.product.slug, filename=filename)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(null=True, upload_to=product_images_dir)
    description = models.CharField(max_length=200, null=False, blank=True)


class Category(MPTTModel):
    title = models.CharField(max_length=100, unique=True, verbose_name='Название')
    temp_name = models.CharField(max_length=50, verbose_name="Видимое название", default='')
    parent = TreeForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='children',
                            db_index=True, verbose_name='Родительская категория')
    slug = models.SlugField(unique=True)
    description = models.TextField(null=True, blank=True, verbose_name='Краткое описание в выборе категорий')
    products_description = models.TextField(null=True, blank=True, verbose_name='Общее описание товаров внутри категории', default='')

    class MPTTMeta:
        order_insertion_by = ['title']

    class Meta:
        unique_together = [['parent', 'slug']]
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def get_absolute_url(self):
        return reverse('shop:product-by-category', args=[str(self.slug)])

    def __str__(self):
        return self.title


def category_images_dir(instance, filename):
    return 'imgs/category_{slug}/{filename}'.format(slug=instance.category.slug, filename=filename)


class CategoryImage(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(null=True, upload_to=category_images_dir)
    description = models.CharField(max_length=200, null=False, blank=True)


class Order(models.Model):
    STATUS_CHOICES = [
        ('processing', 'В обработке'),
        ('agreement', 'Заключение договора'),
        ('paid', 'В работе'),
        ('ready', 'Готов, ожидает отгрузку'),
        ('shipped', 'Отгружен'),
    ]

    DELIVERY_CHOICES = [
        ('company1', 'ТК Деловые линии'),
        ('company2', 'ТК КИТ'),
        ('company3', 'ТК Байкал-Сервис'),
        ('company4', 'Самовывоз'),
        ('company99', 'Сборный груз (проходящая машина), для близлежащих регионов'),
        ('custom', 'Другой вариант'),
    ]

    PAYMENT_CHOICES = [
        ('card', 'Оплата по QR коду'),
        ('transfer_to_card', 'Оплата переводом на карту'),
        ('bank_transfer_with_VAT', 'Банковский перевод с НДС'),
        ('bank_transfer_without_VAT', 'Банковский перевод без НДС'),
        ('card_in_office', 'Оплата картой в офисе'),
        ('cash', 'Оплата наличными в офисе'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    delivery_method = models.CharField(max_length=60, choices=DELIVERY_CHOICES)
    custom_delivery = models.CharField(max_length=200, blank=True, null=True)  # Если пользователь выбрал "Другая компания"
    payment_method = models.CharField(max_length=30, choices=PAYMENT_CHOICES)
    address = models.TextField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} ({self.get_status_display()})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True)
    size_option = models.ForeignKey('SizeOption', on_delete=models.SET_NULL, null=True)
    handle_option = models.ForeignKey('HandleOption', on_delete=models.SET_NULL, null=True)
    threshold = models.CharField(max_length=3, choices=[('да', 'Да'), ('нет', 'Нет')])
    opening_side = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} ({self.quantity} шт.)"