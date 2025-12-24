# apps/bot/bot_runner.py
import os
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

from apps.bot.bot import start

BOT_TOKEN = os.environ.get('BOT_TOKEN', '8299898859:AAECO9ax0qamJNujcaeLdBJYbxt_M3sSWkM')

async def start_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    # app.add_handler(CallbackQueryHandler(vote_callback, pattern="^vote_"))
    await app.run_polling()
