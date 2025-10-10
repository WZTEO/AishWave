from django.contrib import admin
from .models import WithdrawalRequest

@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipient', 'amount', 'status', 'created_at', 'processed_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'recipient__recipient_name')
