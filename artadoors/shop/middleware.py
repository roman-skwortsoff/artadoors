from django.http import JsonResponse
from time import time


class SaveOldSessionKeyMiddleware:
    """Сохраняет старый session_key для анонимных пользователей"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            session_key = request.session.session_key or request.session.create()
            if 'old_session_key' not in request.session:
                request.session['old_session_key'] = session_key
        return self.get_response(request)


class SessionRateLimitMiddleware:
    """
    Middleware для ограничения числа запросов с одной сессии.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Если сессия ещё не существует, создаём её
        if not request.session.session_key:
            request.session.save()

        # Лимитируем только POST-запросы
        if request.method == 'POST':
            # Получаем время запросов из сессии
            request_times = request.session.get('request_times', [])

            # Удаляем старые записи (старше 60 секунд)
            current_time = time()
            request_times = [t for t in request_times if current_time - t < 60]

            # Сохраняем обновленный список запросов
            request_times.append(current_time)
            request.session['request_times'] = request_times

            # Проверяем, превышен ли лимит
            if len(request_times) > 7:  # Например, лимит 7 запросов в минуту
                return JsonResponse(
                    {"error": "Слишком много запросов! Попробуйте позже."},
                    status=429
                )

        # Продолжаем обработку запроса
        return self.get_response(request)
