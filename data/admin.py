from django.contrib import admin
from .models import AccountGrowth, Trade, Order


# Register your models here.]@admin.register(CustomUser)

@admin.register(AccountGrowth)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'balance']


admin.site.register(Trade)
admin.site.register(Order)
