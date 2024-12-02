from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from .models import Product, Category, SizeOption, AdditionalOption, Price, ProductImage, CategoryImage
from django_mptt_admin.admin import DjangoMpttAdmin
class Sizes(admin.TabularInline):
    model = SizeOption
class AdditionalOptions(admin.TabularInline):
    model = AdditionalOption
class ImagesInLine(admin.TabularInline):
    model = ProductImage
class CatImagesInLine(admin.TabularInline):
    model = CategoryImage


@admin.action(description='Archive products')
def mark_archived (modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)

@admin.action(description='Unarchive products')
def mark_unarchived (modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)

class ProductAdmin(admin.ModelAdmin,):
    inlines = [
        Sizes,
        AdditionalOptions,
        ImagesInLine,
               ]
    list_display = 'name', 'slug', 'category', 'description_short', 'archived'
    list_display_links = 'name', 'slug'
    ordering = '-name',
    search_fields = 'name', 'description'
    prepopulated_fields = {"slug": ("name",)}

    def get_fields(self, request, obj=None):
        return ['name', 'category', 'slug', 'archived', 'description', 'base_price', 'sales_sort', 'characteristics', 'archived']

    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + '...'

admin.site.register(Product, ProductAdmin)


class CategoryAdmin(DjangoMpttAdmin):
    prepopulated_fields = {"slug": ("title",), "temp_name": ("title",)}

    inlines = [
        CatImagesInLine,
    ]
admin.site.register(Category, CategoryAdmin)

