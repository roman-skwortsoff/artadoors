from django.contrib import admin
from .models import Profile

# Register your models here.

class ProfileAdmin(admin.ModelAdmin):
    list_display = 'user',  'city', 'birth_date', 'phone_number'     

admin.site.register(Profile, ProfileAdmin)