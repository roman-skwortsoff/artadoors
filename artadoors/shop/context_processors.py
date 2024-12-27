from django.db.models import Sum, Count
from .models import Cart, Favorite

def cart_and_favorites_count(request):
    session_key = request.session.session_key or request.session.create()
    
    # Проверяем наличие старого ключа для анонимного пользователя
    if not request.user.is_authenticated:
        old_session_key = request.session.get('old_session_key')
        if old_session_key:
            session_key = old_session_key

    if request.user.is_authenticated:
        cart_data = Cart.objects.filter(user=request.user).aggregate(
            total_quantity=Sum('quantity'),
            total_items=Count('id')
        )
        favorites_count = Favorite.objects.filter(user=request.user).count()
    else:
        cart_data = Cart.objects.filter(session_key=session_key).aggregate(
            total_quantity=Sum('quantity'),
            total_items=Count('id')
        )
        favorites_count = Favorite.objects.filter(session_key=session_key).count()

    return {
        'cart_count': cart_data['total_quantity'] or 0,  # Общее количество товаров в корзине
        'favorites_count': favorites_count,  # Количество избранных позиций
#        'cart_items_count': cart_data['total_items'] or 0,  # Количество позиций в корзине
    }




#from django.db.models import Sum
#from .models import Cart, Favorite
#
#def cart_and_favorites_count(request):
#    session_key = request.session.session_key or request.session.create()
#    
#    # Проверяем наличие старого ключа для анонимного пользователя
#    if not request.user.is_authenticated:
#        old_session_key = request.session.get('old_session_key')
#        if old_session_key:
#            session_key = old_session_key
#
#    # Избранное и корзина для авторизованных и анонимных
#    if request.user.is_authenticated:
#        cart_count = Cart.objects.filter(user=request.user).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
#        favorites_count = Favorite.objects.filter(user=request.user).count()
#    else:
#        cart_count = Cart.objects.filter(session_key=session_key).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
#        favorites_count = Favorite.objects.filter(session_key=session_key).count()
#
#    # Возвращаем данные в шаблон
#    return {
#        'cart_count': cart_count,
#        'favorites_count': favorites_count,
#    }
#