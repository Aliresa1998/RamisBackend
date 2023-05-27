from django.contrib import admin
from .models import AccountGrowth
# Register your models here.]@admin.register(CustomUser)

@admin.register(AccountGrowth)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'balance']
