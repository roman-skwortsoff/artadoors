# Generated by Django 5.1.2 on 2024-11-24 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='base_price',
            field=models.DecimalField(decimal_places=0, max_digits=10, verbose_name='Начальная цена'),
        ),
        migrations.AlterField(
            model_name='product',
            name='characteristics',
            field=models.JSONField(blank=True, null=True, verbose_name='Характеристики в формате JSON'),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Описание товара'),
        ),
        migrations.AlterField(
            model_name='product',
            name='sales_sort',
            field=models.IntegerField(blank=True, null=True, verbose_name='Порядок сортировки'),
        ),
    ]
