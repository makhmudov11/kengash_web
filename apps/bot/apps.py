# apps/bot/apps.py
from django.apps import AppConfig
import threading
import os
import sys

# Global singleton
_bot_thread = None
_bot_lock = threading.Lock()

class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.bot'

    def ready(self):
        # Faqat asosiy jarayonda ishga tushirish
        if self._is_main_process():
            print("BotConfig ready() → Bot ishga tushmoqda (uvicorn)...")
            self.start_bot_once()

    def _is_main_process(self):
        """uvicorn, gunicorn, hypercorn uchun moslashtirilgan"""
        return (
            # Development: uvicorn main process
            'uvicorn' in sys.argv[0].lower() or
            'hypercorn' in sys.argv[0].lower() or
            # Production: gunicorn master
            os.environ.get('RUN_MAIN') == 'true' or
            # Django runserver
            ('runserver' in sys.argv and 'test' not in sys.argv)
        )

    def start_bot_once(self):
        global _bot_thread
        with _bot_lock:
            if _bot_thread is None or not _bot_thread.is_alive():
                print("Bot thread ishga tushmoqda (singleton)...")
                try:
                    from .bot import run_bot
                    _bot_thread = threading.Thread(target=run_bot, daemon=True)
                    _bot_thread.start()
                    print("Bot muvaffaqiyatli ishga tushdi.")
                except Exception as e:
                    print(f"Bot ishga tushmadi: {e}")
            else:
                print("Bot allaqachon ishlayapti.")