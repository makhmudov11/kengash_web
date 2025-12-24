import decouple
import requests
import asyncio
import threading

from asgiref.sync import sync_to_async
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)

import config.settings
from apps.bot.callback_handler import vote_save_handler, noop_handler
from apps.bot.keyboards import send_voting_keyboard, get_contact_keyboard
from apps.bot.queries import get_user
from apps.bulletin.models import BulletinGroup

BOT_TOKEN = decouple.config('BOT_TOKEN')
BOT_USERNAME = decouple.config('BOT_USERNAME')
GROUP_CHAT_ID = decouple.config('GROUP_CHAT_ID')


_bot_thread = None
_bot_lock = threading.Lock()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_param = context.args[0] if context.args else None
    if not start_param and update.message and "?start=" in update.message.text:
        start_param = update.message.text.split("?start=")[1]

    if not start_param or not start_param.startswith("vote_"):
        await update.message.reply_text("Link noto'g'ri yoki argument yo'q.")
        return

    bulletin_group_id = int(start_param.split("_")[1])
    context.user_data['bulletin_group_id'] = bulletin_group_id

    user_tg_id = update.message.from_user.id

    user_exist = await sync_to_async(get_user)(tg_id=int(user_tg_id))

    if user_exist and user_exist.verified:
        await send_voting_keyboard(update, context, group_id=bulletin_group_id, user_tg_id=user_tg_id)
        return
    elif user_exist and not user_exist.verified:
        await update.message.reply_text(
            "Siz admin tomonidan tasdiqlanmagansiz.",
            reply_markup=None
        )
        return

    await update.message.reply_text(
        "Ovoz berishdan oldin, iltimos, kontakt ma'lumotlaringizni yuboring:",
        reply_markup=get_contact_keyboard()
    )


# KONTAKT QABUL QILISH
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    tg_id = contact.user_id
    phone = contact.phone_number.replace("+", "").replace(" ", "")

    bulletin_group_id = context.user_data.get('bulletin_group_id')
    if not bulletin_group_id:
        await update.message.reply_text("Sessiya tugadi. Qayta boshlang.")
        return

    payload = {
        "tg_id": str(tg_id),
        "phone_number": phone,
        "bulletin_group_id": int(bulletin_group_id)
    }

    try:
        response = await asyncio.to_thread(
            requests.post,
            config.settings.API_VERIFY_URL,
            json=payload,
            timeout=10
        )
        try:
            data = response.json()
        except ValueError:
            await update.message.reply_text("Xatolik: serverdan noto‘g‘ri javob keldi")
            return
        if response.status_code == 200 and data.get("allowed"):
            await update.message.reply_text("Kontakt tasdiqlandi.", reply_markup=None)
            await send_voting_keyboard(update, context, bulletin_group_id, tg_id)
            return
        else:
            await update.message.reply_text(data.get("message", "Ruxsat etilmadi."))
    except Exception as e:
        await update.message.reply_text(f"Xatolik: {e}")


# ------------------ Guruhga yuborish ------------------
def send_bulletin_to_group(bulletin_group: BulletinGroup):
    if bulletin_group.status:
        return {"detail": "Byulleten allaqachon faollashtirilgan!"}

    url = f"https://t.me/{BOT_USERNAME}?start=vote_{bulletin_group.id}"
    keyboard = [[InlineKeyboardButton("Ovoz berish", url=url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"{bulletin_group.name}\nOvoz berish uchun tugmani bosing."

    def _send():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot = Bot(token=BOT_TOKEN)
        try:
            loop.run_until_complete(

                bot.send_message(chat_id=GROUP_CHAT_ID, text=text, reply_markup=reply_markup)

            )
            print(GROUP_CHAT_ID)
            bulletin_group.status = True
            bulletin_group.save()
            print(f"Bulletin {bulletin_group.id} guruhga yuborildi.")
        except Exception as e:
            print(f"Guruhga yuborishda xato: {e}")
        finally:
            loop.close()

    thread = threading.Thread(target=_send, daemon=True)
    thread.start()
    return {"detail": "Yuborish boshlandi..."}


# ------------------ Bot Runner (Singleton) ------------------
def run_bot():
    global _bot_thread
    with _bot_lock:
        if _bot_thread is not None and _bot_thread.is_alive():
            print("Bot allaqachon ishlamoqda.")
            return

        print("Telegram bot ishga tushmoqda...")

        def _start_bot():
            app = ApplicationBuilder().token(BOT_TOKEN).build()

            # HANDLERLAR
            app.add_handler(CommandHandler("start", start))
            app.add_handler(MessageHandler(filters.CONTACT, handle_contact))  # MUHIM!
            app.add_handler(CallbackQueryHandler(vote_save_handler))  # Bitta!
            app.add_handler(CallbackQueryHandler(noop_handler, pattern="^noop$"))

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                loop.run_until_complete(app.initialize())
                loop.run_until_complete(app.start())
                loop.run_until_complete(
                    app.updater.start_polling(
                        drop_pending_updates=True,
                        allowed_updates=Update.ALL_TYPES
                    )
                )
                print("Bot polling boshlandi. Ishlayapti...")
                loop.run_forever()
            except Exception as e:
                print(f"Bot xatosi: {e}")
            finally:
                try:
                    loop.run_until_complete(app.updater.stop())
                    loop.run_until_complete(app.stop())
                    loop.run_until_complete(app.shutdown())
                except:
                    pass
                loop.close()

        _bot_thread = threading.Thread(target=_start_bot, daemon=True)
        _bot_thread.start()
