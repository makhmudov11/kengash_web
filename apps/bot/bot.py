import os

import decouple
import requests
import asyncio
import threading

from asgiref.sync import sync_to_async
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)

from apps.bot.queries import get_user_full_name, get_none_vote_bulletin, get_user_vote_count_in_group, \
    bulletin_group_in_bulletin_count
from apps.bulletin.models import Bulletin, VoteChoices, BulletinGroup

# ------------------ Konfiguratsiya ------------------
BOT_TOKEN = decouple.config('BOT_TOKEN')
BOT_USERNAME = decouple.config('BOT_USERNAME')
GROUP_CHAT_ID = decouple.config('GROUP_CHAT_ID')

# URL'LAR
API_VERIFY_URL = "http://127.0.0.1:8000/api/bot/verify-contact/"  # TO'G'RI!
API_VOTE_URL = "http://127.0.0.1:8000/api/bot/bulletins/vote/"

# ------------------ Singleton Lock ------------------
_bot_thread = None
_bot_lock = threading.Lock()


# ------------------ Keyboard ------------------
def get_contact_keyboard():
    keyboard = [[KeyboardButton("Kontakt yuborish", request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


# ------------------ Handlers ------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_param = context.args[0] if context.args else None
    if not start_param and update.message and "?start=" in update.message.text:
        start_param = update.message.text.split("?start=")[1]

    if not start_param or not start_param.startswith("vote_"):
        await update.message.reply_text("Link noto'g'ri yoki argument yo'q.")
        return

    bulletin_group_id = start_param.split("_")[1]
    context.user_data['bulletin_group_id'] = bulletin_group_id

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


    if isinstance(bulletin_group_id, int):
        pass
    elif isinstance(bulletin_group_id, str) and "_" in bulletin_group_id:
        bulletin_group_id = bulletin_group_id.split("_")[1]
    else:
        # noto'g'ri format
        raise ValueError(f"bulletin_group_id noto'g'ri formatda: {bulletin_group_id}")


    bulletin_group_id = int(bulletin_group_id)
    tg_id = tg_id if isinstance(tg_id, int) else int(tg_id)

    payload = {
        "telegram_id": tg_id,
        "phone_number": phone,
        "bulletin_id": bulletin_group_id
    }

    try:
        response = await asyncio.to_thread(
            requests.post,
            API_VERIFY_URL,
            json=payload,
            timeout=10
        )
        print('salmgas.gml.kam.akms.')
        data = response.json()
    except Exception as e:
        await update.message.reply_text(f"Xatolik: {e}")
        return

    if response.status_code == 200 and data.get("allowed"):
        print("asmasmgklslag;lask")
        # Kontakt tugmasini olib tashlash
        await update.message.reply_text("Kontakt tasdiqlandi ✅", reply_markup=None)
    else:
        print("kasjgk,jnajgnkallasngjan")
        await update.message.reply_text(data.get("message", "Ruxsat etilmadi."))
        return



# # BITTA BUTTON HANDLER (faqat bittasi!)
# async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()
#
#     try:
#         _, bulletin_id, choice = query.data.split("_")
#     except:
#         await query.edit_message_text("Xatolik: Tugma noto'g'ri.")
#         return
#
#     telegram_id = query.from_user.id
#     data = {
#         "bulletin": int(bulletin_id),
#         "choice": choice,
#         "telegram_id": telegram_id
#     }
#
#     try:
#         response = requests.post(API_VOTE_URL, json=data, timeout=10)
#         if response.status_code in [200, 201]:
#             await query.edit_message_text("Ovoz muvaffaqiyatli qabul qilindi!")
#         else:
#             error = response.json() if 'application/json' in response.headers.get('content-type', '') else response.text
#             await query.edit_message_text(f"Xatolik: {error}")
#     except Exception as e:
#         await query.edit_message_text(f"Xatolik: {e}")

# ------------------ Guruhga yuborish ------------------
def send_bulletin_to_group(bulletin: Bulletin):
    if bulletin.status:
        return {"detail": "Byulleten allaqachon faollashtirilgan!"}

    url = f"https://t.me/{BOT_USERNAME}?start=vote_{bulletin.id}"
    keyboard = [[InlineKeyboardButton("Ovoz berish", url=url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"{bulletin.name}\nOvoz berish uchun tugmani bosing."

    def _send():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot = Bot(token=BOT_TOKEN)
        try:
            loop.run_until_complete(
                bot.send_message(chat_id=GROUP_CHAT_ID, text=text, reply_markup=reply_markup)
            )
            bulletin.status = True
            bulletin.save()
            print(f"Bulletin {bulletin.id} guruhga yuborildi.")
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
            # app.add_handler(CallbackQueryHandler(button))  # Bitta!

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
