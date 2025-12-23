from django.db import models

from apps.employee.models import Employee


class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True, db_index=True)
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='telegram_accounts'
    )
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'bot'  # MUHIM!
        verbose_name = "Telegram foydalanuvchi"
        verbose_name_plural = "Telegram foydalanuvchilar"
        indexes = [
            models.Index(fields=['telegram_id']),
            models.Index(fields=['employee']),
        ]

    def __str__(self):
        name = self.employee.full_name if self.employee else "Bog'lanmagan"
        return f"@{self.telegram_id} → {name}"

    def verify(self):
        self.is_verified = True
        self.save(update_fields=['is_verified', 'updated_at'])
