from cProfile import label

from django import forms
from django.contrib.auth.models import User
from django.core import validators
from django.core.validators import RegexValidator
from .models import Profile
import datetime
from django.contrib.auth.forms import PasswordChangeForm


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
    verification_code = forms.CharField(
        label='Код подтверждения', required=False,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )

    def clean(self):
        cleaned_data = super().clean()

        # Проверяем, что все обязательные поля заполнены и валидны
        if not all(cleaned_data.get(field) for field in ['username', 'password', 'first_name', 'last_name']):
            raise forms.ValidationError("Заполните все поля корректно перед подтверждением email.")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-input'

    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name')

    username = forms.EmailField(label='Email', validators=[validators.validate_email])
    password = forms.CharField(label='Пароль', validators=[validators.RegexValidator(r'^(?!\d+$).+', 'Пароль не должен быть из цифр'), validators.MinLengthValidator(8, "Введённый пароль слишком короткий. Он должен содержать как минимум 8 символов")],
                               widget=forms.PasswordInput)
    first_name = forms.CharField(label='Имя', validators=[validators.RegexValidator(r'^[А-Яа-я]', 'Только русскими буквами, не должно быть пустым'), validators.MinLengthValidator(2, "Неверный ввод")])
    last_name = forms.CharField(label='Фамилия', validators=[validators.RegexValidator(r'^[А-Яа-я]', 'Только русскими буквами, не должно быть пустым')])


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

month_choices = [
    ('1', 'Январь'), ('2', 'Февраль'), ('3', 'Март'), ('4', 'Апрель'),
    ('5', 'Май'), ('6', 'Июнь'), ('7', 'Июль'), ('8', 'Август'),
    ('9', 'Сентябрь'), ('10', 'Октябрь'), ('11', 'Ноябрь'), ('12', 'Декабрь')
]

class ProfileUpdateForm(forms.ModelForm):
    day = forms.ChoiceField(
        choices=[(str(i), str(i)) for i in range(1, 32)], 
        label='День', 
        required=False
    )
    month = forms.ChoiceField(
        choices=month_choices,
        label='Месяц',
        required=False
    )
    year = forms.ChoiceField(
        choices=[(str(i), str(i)) for i in range((datetime.date.today().year)-16, 1925, -1)],
        label='Год',
        required=False
    )

    class Meta:
        model = Profile
        fields = ['city', 'phone_number']  # Исключаем birth_date

    phone_number = forms.CharField(label='Номер телефона', validators=[validators.RegexValidator(r'^((\+7|8)[-\s]?)?(\(?\d{3}\)?[-\s]?)?\d{3}[-\s]?\d{2}[-\s]?\d{2}$', 'Корректный номер телефона!')])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Если уже есть дата рождения, разбиваем её на компоненты
        if self.instance.birth_date:
            self.fields['day'].initial = self.instance.birth_date.day
            self.fields['month'].initial = self.instance.birth_date.month
            self.fields['year'].initial = self.instance.birth_date.year

    def clean(self):
        cleaned_data = super().clean()
        day = cleaned_data.get('day')
        month = cleaned_data.get('month')
        year = cleaned_data.get('year')

        if day and month and year:
            try:
                birth_date = datetime.date(int(year), int(month), int(day))
                cleaned_data['birth_date'] = birth_date
            except ValueError:
                self.add_error('day', 'Некорректная дата')
        return cleaned_data

    def save(self, commit=True):
        profile = super().save(commit=False)
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            profile.birth_date = birth_date
        if commit:
            profile.save()
        return profile

class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Старый пароль", widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password1 = forms.CharField(label="Новый пароль", widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password2 = forms.CharField(label="Подтверждение пароля", widget=forms.PasswordInput(attrs={'class': 'form-input'}))