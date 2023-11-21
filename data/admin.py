from django.contrib import admin
from .models import AccountGrowth, Trade, Order, Wallet


# Register your models here.]@admin.register(CustomUser)

@admin.register(AccountGrowth)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'balance']


admin.site.register(Trade)
admin.site.register(Order)
admin.site.register(Wallet)
