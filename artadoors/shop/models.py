from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey


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


def product_images_dir(instance, filename):
    return 'static/imgs/product_{slug}/{filename}'.format(slug=instance.product.slug, filename=filename)

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
    return 'static/imgs/category_{slug}/{filename}'.format(slug=instance.category.slug, filename=filename)


class CategoryImage(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(null=True, upload_to=category_images_dir)
    description = models.CharField(max_length=200, null=False, blank=True)