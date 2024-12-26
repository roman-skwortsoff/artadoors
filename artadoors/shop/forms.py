from django import forms
from .models import Product, SizeOption, HandleOption


class ProductDetailForm(forms.Form):
    # Поле для выбора размера
    Размер = forms.ModelChoiceField(
        queryset=None,  # Сначала пустой запрос, позже будет заполняться в представлении
        empty_label="Выберите размер",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'size-select'})
    )

    # Поле для выбора ручки
    Ручка = forms.ModelChoiceField(
        queryset=None,  # Сначала пустой запрос, позже будет заполняться в представлении
        empty_label="Выберите ручку",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'handle-select'})
    )

    Порог = forms.ChoiceField(
        choices=[('нет', 'Нет'), ('да', 'Да')],
        widget=forms.RadioSelect(attrs={'id': 'threshold-select'}),
        initial='нет',  # По умолчанию "нет"
        label="Добавить порог"
    )

    # Поле выбора стороны открывания
    Открывание = forms.ChoiceField(
        choices=[
            ('Правое (на себя, петли справа)', 'Правое (на себя, петли справа)'),
            ('Левое (на себя, петли слева)', 'Левое (на себя, петли слева)')
        ],
        widget=forms.RadioSelect(attrs={'id': 'opening-side-select'}),
        initial='Правое (на себя, петли справа)',
        label="Сторона открывания"
    )

    Количество = forms.IntegerField(
        min_value=1,  # Минимальное количество
        max_value=30,  # Максимальное количество (можно настроить)
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'quantity-input'}),
        initial=1,  # Значение по умолчанию
        label="Количество"
    )

    def __init__(self, *args, **kwargs):
        product = kwargs.pop('product', None)  # Получаем продукт, для которого заполняем форму
        super().__init__(*args, **kwargs)
        if product:
            # Заполняем queryset доступных размеров для конкретного продукта
            size_options = SizeOption.objects.filter(product=product)
            self.fields['Размер'].queryset = size_options

            # Заполняем queryset доступных ручек для конкретного продукта
            handle_options = HandleOption.objects.filter(products=product)
            self.fields['Ручка'].queryset = handle_options
