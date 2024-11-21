from cProfile import label

from django import forms
from django.contrib.auth.models import User
from django.core import validators
from django.core.validators import RegexValidator


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        try:
            self.user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError(f'Пользователь по почте {username} не найден!')

        if not self.user.check_password(password):
            raise forms.ValidationError(f'Пароль для {username} введен неверно!')


class RegisterForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-input'

    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name')

    username = forms.EmailField(label='Email', validators=[validators.validate_email])
    password = forms.CharField(label='Пароль', validators=[validators.MinLengthValidator(4, "Минимум 4 знака/буквы/цифры")],
                               widget=forms.PasswordInput)
    first_name = forms.CharField(label='Имя', validators=[validators.RegexValidator(r'^[А-Яа-я]', 'Только русскими буквами, не должно быть пустым'), validators.MinLengthValidator(2, "Неверный ввод")])
    last_name = forms.CharField(label='Фамилия', validators=[validators.RegexValidator(r'^[А-Яа-я]', 'Только русскими буквами, не должно быть пустым')])