# apps/bot/management/commands/bot_status.py
from django.core.management.base import BaseCommand

from bot.apps import BotConfig


class Command(BaseCommand):
    help = 'Bot holatini tekshirish'

    def handle(self, *args, **options):
        status = BotConfig.get_bot_status()
        if status:
            self.stdout.write(self.style.SUCCESS('✅ Bot ishlayapti'))
        else:
            self.stdout.write(self.style.ERROR('❌ Bot ishlamayapti'))