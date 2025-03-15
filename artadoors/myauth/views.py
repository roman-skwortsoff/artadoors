from django.contrib.auth import logout, authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileUpdateForm, UserPasswordChangeForm, LoginForm, RegisterForm
from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from django.contrib.auth.models import User
from .models import Profile
from shop.models import Cart, Favorite, Order, OrderItem
from django.contrib import messages
from django.http import JsonResponse, HttpRequest, HttpResponse, HttpResponseForbidden
import random
from .tasks import send_password_reset_email, send_verification_email, send_reg_message
from django.urls import reverse, reverse_lazy
from django.core.cache import cache
from django.utils.timezone import now
from datetime import timedelta


def login_user(request):
    context = {'login_form': LoginForm()}
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            # Сохраняем old_session_key
            session_key = request.session.session_key or request.session.create()
            request.session['old_session_key'] = session_key
            #print("[LOGIN] Сохранен old_session_key:", session_key)

            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('index')
            else:
                context = {
                    'login_form': login_form,
                    'attention': f'Пользователь {username} и пароль не найдены!'
                }
        else:
            context = {
                'login_form': login_form,
            }
    return render(request, 'user/login.html', context)


class RegisterView(TemplateView):
    template_name = 'user/register.html'

    def get(self, request):
        user_form = RegisterForm()
        return render(request, self.template_name, {'user_form': user_form})
    
    def post(self, request):          
        #print("[POST] Получен запрос:", request.POST)  # Логируем весь POST-запрос
        user_form = RegisterForm(request.POST)
        entered_code = request.POST.get('verification_code')

        # 1. Нажали «Подтвердить Email» → Генерируем код
        if entered_code == '000':
            #print("[POST] Нажата кнопка Подтвердить E-mail")  
            
            if user_form.is_valid():
                email = user_form.cleaned_data['username']
                verification_code = random.randint(100000, 999999)   
                request.session['verification_code'] = str(verification_code)
                request.session['user_data'] = user_form.cleaned_data

                # Отправляем код асинхронно
                send_verification_email(email, verification_code) 
    
                return JsonResponse({'status': 'ok', 'message': 'Код отправлен на email!'})
    
            #print("[POST] Ошибки формы:", user_form.errors)
            return JsonResponse({"status": "error", "errors": user_form.errors}, status=400)  # <-- Возвращаем JSON!
        
        # 2. Если код уже сохранен в сессии, проверяем, соответствует ли введенный код
        session_code = request.session.get('verification_code')

        if session_code and entered_code == session_code:
            #print("[POST] Введенный код совпадает, регистрируем пользователя")

            # Получаем сохраненные данные пользователя
            user_data = request.session.get('user_data', {})

            # Создаем пользователя
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['username'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )

            send_reg_message(user_data['username'])
    
            session_key = request.session.session_key or request.session.create()
            request.session['old_session_key'] = session_key
    
            #print("[POST] Сохранен old_session_key:", session_key)
    
            login(request, user)
    
            request.session.pop('verification_code', None)
            request.session.pop('user_data', None)

            return JsonResponse({'status': 'ok', 'redirect_url': reverse('edit_user')})

        # 3. Если код не совпадает или отсутствует, возвращаем ошибку    
        #print("[POST] Некорректный запрос")
        return JsonResponse({'status': 'error', 'message': 'Введен неверный код'}, status=400)
    

def logout_user(request):
    logout(request)
    return redirect('index')


@login_required
def user_detail(request):
    profile = getattr(request.user, 'profile', None)
    if not profile:
        Profile.objects.create(user=request.user)  # Создаем профиль, если его нет
    orders = Order.objects.filter(user=request.user)
    #print(orders)    
    return render(request, 'user/user_detail.html', {'orders': orders})


@login_required
def user_order(request: HttpRequest, pk: int) -> HttpResponse:
    order = get_object_or_404(Order, id=pk)

    # Проверяем, что заказ принадлежит текущему пользователю или сессии
    if request.user.is_authenticated:
        if order.user != request.user:
            return HttpResponseForbidden("У вас нет доступа к этому заказу.")
    else:
        session_key = request.session.session_key
        if order.session_key != session_key:
            return HttpResponseForbidden("У вас нет доступа к этому заказу.")
    
    # Если всё в порядке, отобразить заказ
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'user/user_order.html', {'order': order, 'order_items': order_items})


@login_required
def edit_user(request):
    profile = getattr(request.user, 'profile', None)
    create_profile = False
    if not profile:
        Profile.objects.create(user=request.user)  # Создаем профиль, если его нет
        create_profile = True
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Ваши данные успешно сохранены.')
            return redirect('user_detail')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'create_profile': create_profile
    }
    return render(request, 'user/edit_user.html', context)


class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("password_change_done")
    template_name = "user/password_change_form.html"


class CustomPasswordResetView(PasswordResetView):

    #Модифицированный PasswordResetView с ограничением частоты отправки писем.

    template_name = "user/password_reset_form.html"
    email_template_name = "user/password_reset_email.html"
    success_url = reverse_lazy("password_reset_done")
    timeout = 60  # Время блокировки повторной отправки (в секундах)

    def form_valid(self, form):
        domain = self.request.get_host()
        use_https = self.request.is_secure()
        email = form.cleaned_data["email"]

        cache_key = f"password_reset_{email}"
        last_request_time = cache.get(cache_key)

        if last_request_time:
            form.add_error(None, "Вы недавно уже запрашивали сброс пароля. Попробуйте позже.")
            return self.form_invalid(form)

        # Сохраняем метку времени последней отправки в кэше
        cache.set(cache_key, now(), self.timeout)

        for user in form.get_users(email):
            send_password_reset_email.delay(user.email, domain, use_https)

        return super().form_valid(form)