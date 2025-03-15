from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model

@shared_task
def send_password_reset_email(email, domain, use_https):
    """
    Асинхронная задача для отправки письма с инструкцией по сбросу пароля.
    """
    User = get_user_model()
    user = User.objects.filter(email=email).first()
    if not user:
        return False  # Если пользователя нет, ничего не делаем

    # Генерируем токен для сброса пароля
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    # Определяем протокол (http или https)
    scheme = "https" if use_https else "http"

    # Формируем ссылку для сброса пароля
    reset_url = f"{scheme}://{domain}{reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})}"

    # Генерируем текст письма
    subject = "Восстановление пароля"
    message = render_to_string("user/password_reset_email.html", {"reset_url": reset_url, "user": user})
    
    # Отправляем письмо
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
    return True


@shared_task
def send_verification_email(email, code):
    subject = "Подтверждение регистрации на сайте skwortsoff.twilightparadox.com"
    message = f"Здравствуйте! Ваш код подтверждения регистрации: {code}"
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [email])
    return f"Email sent to {email}"

@shared_task
def send_reg_message(email):
    subject = "Успешная регистрация на сайте skwortsoff.twilightparadox.com"
    message = (
    "Здравствуйте!\n\n"
    "Вы успешно зарегистрировались на сайте. Благодарю вас за интерес к проекту!\n\n"
    "Если у вас возникли вопросы, или вы хотите узнать больше, свяжитесь со мной удобным для вас способом — "
    "контакты указаны на сайте. Вы также можете просто ответить на это письмо.\n\n"
    "С наилучшими пожеланиями!")
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [email])
    return f"Email sent to {email}"