# apps/bot/management/commands/runbot.py
from django.core.management.base import BaseCommand

from bot.bot import run_bot


class Command(BaseCommand):
    help = 'Run Telegram bot'

    def handle(self, *args, **kwargs):
        run_bot()
