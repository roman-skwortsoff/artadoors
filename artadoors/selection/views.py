from django.shortcuts import render
from formtools.wizard.views import SessionWizardView
from django.shortcuts import redirect
from .forms import Step1Form, Step6Form, Step7WoodenForm, Step11AluminumForm

def big_dimensions(request):
    return render(request, 'selection/big-dimensions.html')

def vertical_handle(request):
    return render(request, 'selection/vertical-handle.html')

def wc_lock(request):
    return render(request, 'selection/wc-lock.html')

def black(request):
    return render(request, 'selection/black.html')

def aspen_linden(request):
    return render(request, 'selection/aspen-linden.html')

def alder(request):
    return render(request, 'selection/alder.html')

def thermo_alder(request):
    return render(request, 'selection/thermo-alder.html')

def standart(request):
    return render(request, 'selection/standart.html')

def elit(request):
    return render(request, 'selection/elit.html')

def prestizh(request):
    return render(request, 'selection/prestizh.html')



FORMS = [
    ("step1", Step1Form),
    ("step6", Step6Form),
    ("step7_wooden", Step7WoodenForm),
    ("step11_aluminum", Step11AluminumForm),
]

TEMPLATES = {
    "step1": "selection/step1.html",
    "step6": "selection/step6.html",
    "step7_wooden": "selection/step7_wooden.html",
    "step11_aluminum": "selection/step11_aluminum.html",
}

class DoorSelectionWizard(SessionWizardView):
    form_list = FORMS
    template_name = "wizard.html"

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_form_list(self):
        """
        Определяем динамический список форм в зависимости от данных предыдущих шагов.
        """
        # Получаем базовый список форм
        form_list = super().get_form_list()
        print('hello - get_form_list called')

    
        # Если данных для step1 еще нет, возвращаем все формы (начало процесса)
        step1_data = self.storage.get_step_data('step1')
        print(f'step1_data: {step1_data}')  # Проверим, что приходит из хранилища
    
        if not step1_data:
            print('Returning full form list as step1 data is missing')
            return form_list
    
        requirement = step1_data.get('step1-requirement')
        print(f'step1 requirement: {requirement}')  # Проверим выбор пользователя на step1
    
        # Обработка выбора на step1
        if requirement in ['black_fittings', 'big_dimensions', 'vertical_handle', 'wc_lock']:
            print('Processing specific requirement, skipping unnecessary steps')
            return {'step1': form_list['step1']}
        
        if requirement == 'no_requirements':
            step6_data = self.storage.get_step_data('step6')
            print(f'step6_data: {step6_data}')  # Проверим данные step6
            if not step6_data:
                print('Adding step6 form')
                return {
                    'step1': form_list['step1'],
                    'step6': form_list['step6'],
                }
    
            box_type = step6_data.get('step6-box_type')
            print(f'box_type: {box_type}')  # Проверим выбор пользователя на step6
            if box_type == 'wooden':
                print('Adding step7_wooden form')
                return {
                    'step1': form_list['step1'],
                    'step6': form_list['step6'],
                    'step7_wooden': form_list['step7_wooden'],
                }
            elif box_type == 'aluminum':
                print('Adding step11_aluminum form')
                return {
                    'step1': form_list['step1'],
                    'step6': form_list['step6'],
                    'step11_aluminum': form_list['step11_aluminum'],
                }
    
        print('Defaulting to full form list')
        return form_list


    def done(self, form_list, **kwargs):
        """
        Обрабатываем результаты и перенаправляем в зависимости от выбора.
        """
        data = {form.prefix: form.cleaned_data for form in form_list}

        # Логика обработки выбора
        step1_choice = data.get('step1', {}).get('requirement')
        if step1_choice == 'black_fittings':
            return redirect('select:black')
        elif step1_choice == 'big_dimensions':
            return redirect('select:big_dimensions')
        elif step1_choice == 'vertical_handle':
            return redirect('select:vertical_handle')
        elif step1_choice == 'wc_lock':
            return redirect('select:wc_lock')
        elif step1_choice == 'no_requirements':
            box_type = data.get('step6', {}).get('box_type')
            if box_type == 'wooden':
                material = data.get('step7_wooden', {}).get('material')
                if material == 'aspen_linden':
                    return redirect('select:aspen_linden')
                elif material == 'alder':
                    return redirect('select:alder')
                elif material == 'thermo_alder':
                    return redirect('select:thermo_alder')
            elif box_type == 'aluminum':
                variant = data.get('step11_aluminum', {}).get('variant')
                if variant == 'standart':
                    return redirect('select:standart')
                elif variant == 'elit':
                    return redirect('select:elit')
                elif variant == 'prestizh':
                    return redirect('select:prestizh')
        
        return redirect('/')
