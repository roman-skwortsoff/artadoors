from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from .models import Product, Category, SizeOption, HandleOption, ProductImage, CategoryImage, Favorite, Cart, Order, OrderItem
from django_mptt_admin.admin import DjangoMpttAdmin


class Sizes(admin.TabularInline):
    model = SizeOption
class HandleOptions(admin.TabularInline):
    model = HandleOption
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
        HandleOptions,
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

class FavoriteAdmin(admin.ModelAdmin):
    list_display = 'user', 'session_key', 'product', 'size_option', 'handle_option', 'threshold', 'opening_side', 'price', 'added_at'

admin.site.register(Favorite, FavoriteAdmin)

class CartAdmin(admin.ModelAdmin):
    list_display = 'user', 'session_key', 'product', 'size_option', 'handle_option', 'threshold', 'opening_side', 'price', 'added_at'

admin.site.register(Cart, CartAdmin)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = 'id', 'user', 'session_key', 'last_name', 'first_name', 'total_price', 'created_at'

    def get_fields(self, request, obj=None):
        return ['id', 'user', 'session_key', 'last_name', 'first_name', 'total_price', 'created_at']

    readonly_fields = ('id', 'user', 'session_key', 'last_name', 'first_name', 'total_price', 'created_at')
