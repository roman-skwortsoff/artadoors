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
