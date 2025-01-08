from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    city = models.CharField(max_length=100, verbose_name='Город')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    phone_number = models.CharField(max_length=16, verbose_name='Номер телефона', blank=True)

    def __str__(self):
        return f'Профиль пользователя {self.user.username}'
