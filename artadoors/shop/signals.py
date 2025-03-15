from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Cart, Favorite

@receiver(user_logged_in)
def sync_cart_and_favorites_on_login(sender, request, user, **kwargs):
    session_key = request.session.session_key
    old_session_key = request.session.pop('old_session_key', None)

    #print(f"[LOGIN] Пользователь вошел. old_session_key: {old_session_key}")
    #print(f"[LOGIN] Текущий session_key: {session_key}")

    if old_session_key:
        # Синхронизация корзины
        #print("[SYNC] Начало синхронизации корзины.")
        session_cart_items = Cart.objects.filter(session_key=old_session_key, user__isnull=True)

        for item in session_cart_items:
            # Проверяем, существует ли уже этот товар в корзине пользователя
            cart_item = Cart.objects.filter(
                user=user,
                product=item.product,
                size_option=item.size_option,
                handle_option=item.handle_option,
                threshold=item.threshold,
                opening_side=item.opening_side,
            ).first()

            if cart_item:
                # Если товар уже в корзине, увеличиваем количество
                cart_item.quantity += item.quantity
                cart_item.price += item.price
                cart_item.save()
            else:
                # Если товара нет, переносим его
                item.user = user
                item.session_key = None  # Убираем привязку к сессии
                item.save()

        # Удаляем старые записи из корзины
        session_cart_items.delete()
        #print("[SYNC] Синхронизация корзины завершена.")

        # Синхронизация избранного
        #print("[SYNC] Начало синхронизации избранного.")
        session_favorites = Favorite.objects.filter(session_key=old_session_key, user__isnull=True)

        for item in session_favorites:
            # Проверяем, есть ли товар уже в избранном у пользователя
            favorite_exists = Favorite.objects.filter(
                user=user,
                product=item.product,
                size_option=item.size_option,
                handle_option=item.handle_option,
                threshold=item.threshold,
                opening_side=item.opening_side,
            ).exists()

            if not favorite_exists:
                item.user = user
                item.session_key = None  # Убираем привязку к сессии
                item.save()

        # Удаляем старые записи из избранного
        session_favorites.delete()
        #print("[SYNC] Синхронизация избранного завершена.")
    else:
        print(f"[LOGIN] Старый session_key отсутствует. Синхронизация не выполнена.")
