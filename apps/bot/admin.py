from django.contrib import admin

from .models import TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'employee', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('telegram_id', 'employee__full_name', 'employee__tg_id')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('employee',)

    fieldsets = (
        ('Telegram', {
            'fields': ('telegram_id', 'is_verified')
        }),
        ('Bog\'lanish', {
            'fields': ('employee',),
        }),
        ('Sana', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def has_add_permission(self, request):
        return False
