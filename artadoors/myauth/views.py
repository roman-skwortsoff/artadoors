
from django.contrib.auth import logout, authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from myauth.forms import LoginForm, RegisterForm
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile
from shop.models import Cart, Favorite, Order, OrderItem  # Импорт моделей корзины и избранного
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden


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
            print("[LOGIN] Сохранен old_session_key:", session_key)

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
        context = {'user_form': user_form}
        return render(request, 'user/register.html', context)

    def post(self, request):
        user_form = RegisterForm(request.POST)
        if user_form.is_valid():
            # Создаем пользователя
            user = user_form.save()
            user.set_password(user.password)
            user.email = user_form.cleaned_data['username']
            user.save()

            # Сохраняем old_session_key
            session_key = request.session.session_key or request.session.create()
            request.session['old_session_key'] = session_key
            print("[REGISTER] Сохранен old_session_key:", session_key)

            # Логиним пользователя
            login(request, user)

            return redirect('edit_user')

        context = {'user_form': user_form}
        return render(request, 'user/register.html', context)


def logout_user(request):
    logout(request)
    return redirect('index')


@login_required
def user_detail(request):
    profile = getattr(request.user, 'profile', None)
    if not profile:
        Profile.objects.create(user=request.user)  # Создаем профиль, если его нет
    orders = Order.objects.filter(user=request.user)
    print(orders)    
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
    if not profile:
        Profile.objects.create(user=request.user)  # Создаем профиль, если его нет
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
        'profile_form': profile_form
    }
    return render(request, 'user/edit_user.html', context)
