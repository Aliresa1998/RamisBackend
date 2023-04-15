from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'image', 'is_admin', 'user_id']