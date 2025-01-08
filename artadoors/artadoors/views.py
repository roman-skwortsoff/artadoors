from django.shortcuts import render


def index(request):
    if not request.session.session_key:
        request.session.save()
    return render(request, 'index.html')
