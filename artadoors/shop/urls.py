"""
URL configuration for artadoors project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.views.static import serve
from django.urls import include, path
from .views import show_category, catalog, view_product, favorites_view, cart_view, order_view

from django.urls import path


app_name = 'shop'

urlpatterns = [
    path("catalog/<slug:category_slug>/", show_category, name='product-by-category'),
    path('catalog/', catalog, name='catalog'),
    path("product/<slug:product_slug>/", view_product, name='product-view'),
    path('favorites/', favorites_view, name='favorites'),
    path('cart/', cart_view, name='cart'),
    path('cart/order/', order_view, name='order'),
]
