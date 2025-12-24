from django.contrib import admin

from apps.bot.bot import send_bulletin_to_group
from apps.bot.models import TelegramUser
from apps.bulletin.models import Bulletin, BulletinVote, BulletinGroup


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

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse, path
from django.utils.html import format_html





@admin.register(Bulletin)
class BulletinAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'specialization', 'title', 'created_at', 'created_by', 'agree_count', 'disagree_count')
    list_filter = ( 'title', 'created_at')
    search_fields = ('full_name', 'specialization')
    readonly_fields = ('created_at', 'agree_count', 'disagree_count')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('full_name', 'specialization', 'title', 'status')
        }),
        ('Qo\'shimcha', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',),
        }),
        ('Statistika', {
            'fields': ('agree_count', 'disagree_count'),
            'classes': ('collapse',),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Edit qilganda
            return self.readonly_fields + ('created_by',)
        return self.readonly_fields


@admin.register(BulletinVote)
class BulletinVoteAdmin(admin.ModelAdmin):
    list_display = ('bulletin', 'telegram_id', 'telegram_user', 'choice', 'voted_at')
    list_filter = ('choice', 'voted_at', 'bulletin__title')
    search_fields = ('telegram_id', 'bulletin__full_name',  'telegram_user__employee__full_name')
    readonly_fields = ('voted_at',)
    date_hierarchy = 'voted_at'

    def has_add_permission(self, request):
        # Ovoz faqat bot orqali qo'shiladi
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(BulletinGroup)
class BulletinGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'send_to_telegram_link')
    list_display_links = ('name',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('send/<int:group_id>/', self.admin_site.admin_view(self._send_to_telegram), name='send_to_telegram'),
        ]
        return custom_urls + urls

    def send_to_telegram_link(self, obj):
        if obj.status:
            return "✅ Yuborilgan"
        url = reverse('admin:send_to_telegram', args=[obj.pk])
        return format_html('<a class="button" href="{}">Jonatish</a>', url)

    send_to_telegram_link.short_description = "Guruhga yuborish"
    send_to_telegram_link.allow_tags = True

    def _send_to_telegram(self, request, group_id):
        group = BulletinGroup.objects.get(pk=group_id)
        result = send_bulletin_to_group(group)
        self.message_user(request, f"{group.name.title()} uchun sorovnoma")
        return redirect(request.META.get('HTTP_REFERER'))

