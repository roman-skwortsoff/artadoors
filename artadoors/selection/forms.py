from django import forms

class Step1Form(forms.Form):
    requirement = forms.ChoiceField(
        choices=[
            ('black_fittings', 'Дверь с черной фурнитурой'),
            ('big_dimensions', 'Высота проема 2,1 метра, или ширина проема 0,9 метра и больше'),
            ('vertical_handle', 'Дверь с вертикальной ручкой'),
            ('wc_lock', 'Дверь с WC замком'),
            ('no_requirements', 'Нет таких требований'),
        ],
        widget=forms.RadioSelect,
        label="Особые требования"
    )

class Step6Form(forms.Form):
    box_type = forms.ChoiceField(
        choices=[
            ('wooden', 'Деревянная'),
            ('aluminum', 'Алюминиевая'),
        ],
        widget=forms.RadioSelect,
        label="Тип дверной коробки"
    )

class Step7WoodenForm(forms.Form):
    material = forms.ChoiceField(
        choices=[
            ('aspen_linden', 'Осина/липа'),
            ('alder', 'Ольха'),
            ('thermo_alder', 'Термоольха'),
        ],
        widget=forms.RadioSelect,
        label="Материал деревянной коробки"
    )

class Step11AluminumForm(forms.Form):
    variant = forms.ChoiceField(
        choices=[
            ('standart', 'Хамам Стандарт фото дверь короб петли'),
            ('elit', 'Хамам Элит фото дверь короб петли'),
            ('prestizh', 'Хамам Престиж фото дверь короб петли'),
        ],
        widget=forms.RadioSelect,
        label="Варианты алюминиевой коробки"
    )
