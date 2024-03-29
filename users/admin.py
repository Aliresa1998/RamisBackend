from django.contrib import admin
from .models import CustomUser, Ticket, Plan, CryptoPayment


@admin.register(CustomUser)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'is_admin', 'user_id']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'created_at', 'status']


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['plan', 'amount', 'is_delete']

admin.site.register(CryptoPayment)