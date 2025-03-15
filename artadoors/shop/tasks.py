from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_user_order_message(email, total_price):
    subject = "Вы сделали заказ на сайте skwortsoff.twilightparadox.com"
    message = (
    "Здравствуйте! Это письмо сформировано автоматическим сервисом и демонстрирует функцию автоматических оповещений.\n\n"
    f"Вы оформили заказ на сумму {total_price} руб.")
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [email])
    print(subject, message, from_email, [email])
    return f"Email sent to {email}"

@shared_task
def send_order_message(email, total_price):
    subject = "Вы сделали заказ на сайте skwortsoff.twilightparadox.com"
    message = (
    'Здравствуйте! Это письмо сформировано автоматическим сервисом и демонстрирует функцию автоматических оповещений.\n\n'
    f'Вы оформили заказ на сумму {total_price} руб.\n\n'
    'Вы можете подробнее ознакомиться с проектом на вкладке "О сайте", или по ссылке https://skwortsoff.twilightparadox.com/about/ '
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [email])
    print(subject, message, from_email, [email])
    return f"Email sent to {email}"