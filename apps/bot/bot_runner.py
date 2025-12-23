import django
from telegram.ext import ApplicationBuilder, CommandHandler
import os

from apps.bot.bot import start

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
import config.settings



async def start_bot():
    app = ApplicationBuilder().token(config.settings.BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    # app.add_handler(CallbackQueryHandler(vote_callback, pattern="^vote_"))
    await app.run_polling()
