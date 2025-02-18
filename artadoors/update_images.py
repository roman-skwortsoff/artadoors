import os
import django

# Указываем Django, какой файл настроек использовать
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artadoors.settings.dev')
django.setup()

from shop.models import ProductImage, CategoryImage
# Обновляем пути для всех изображений
for product_image in ProductImage.objects.all():
    if product_image.image.name.startswith('static/imgs/'):
        product_image.image.name = product_image.image.name.replace('static/imgs/', 'imgs/')
        product_image.save()


for category_image in CategoryImage.objects.all():
    if category_image.image.name.startswith('static/imgs/'):
        category_image.image.name = category_image.image.name.replace('static/imgs/', 'imgs/')
        category_image.save()