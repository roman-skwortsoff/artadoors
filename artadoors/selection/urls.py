from django.urls import include, path
from .views import (DoorSelectionWizard, black, big_dimensions, vertical_handle,
                    wc_lock, aspen_linden, alder, thermo_alder, standart,
                    elit, prestizh)


app_name = 'select'

urlpatterns = [
    path('', DoorSelectionWizard.as_view(), name='door_selection'),
    path('black/', black, name='black'),
    path('big-dimensions/', big_dimensions, name='big_dimensions'),
    path('vertical-handle/', vertical_handle, name='vertical_handle'),
    path('wc-lock/', wc_lock, name='wc_lock'),
    path('aspen-linden/', aspen_linden, name='aspen_linden'),
    path('alder/', alder, name='alder'),
    path('thermo-alder/', thermo_alder, name='thermo_alder'),
    path('standart/', standart, name='standart'),
    path('elit/', elit, name='elit'),
    path('prestizh', prestizh, name='prestizh'),
]
