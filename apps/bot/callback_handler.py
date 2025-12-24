import asyncio

import requests
from asgiref.sync import sync_to_async


from telegram import Update
from telegram.ext import  ContextTypes

from apps.bot.queries import get_user_full_name
from apps.bulletin.models import VoteChoices


async def noop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()



from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def vote_save_handler(update: Update, context):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "submit":
        await query.answer("Ovozlar tasdiqlandi ✅", show_alert=True)

        await query.edit_message_text(
            text="✅ Ovoz berish yakunlandi.\n\nRahmat, sizning ovozingiz qabul qilindi."
        )

        await query.edit_message_reply_markup(reply_markup=None)

        return

    if data == "noop":
        await query.answer("Bu variant allaqachon tanlangan ❌", show_alert=True)
        return

    try:
        bulletin_id, choice = data.split("_")
    except ValueError:
        await query.answer("❌ Noto‘g‘ri tugma", show_alert=True)
        return

    telegram_id = query.from_user.id

    payload = {
        "bulletin": int(bulletin_id),
        "choice": choice,
        "telegram_id": telegram_id
    }

    api_vote_url = "http://127.0.0.1:8000/api/bot/bulletins/vote/"

    response = await asyncio.to_thread(
        requests.post,
        api_vote_url,
        json=payload,
        timeout=10
    )

    if response.status_code not in (200, 201):
        await query.answer("❌ Ovozni saqlab bo‘lmadi", show_alert=True)
        return

    old_keyboard = query.message.reply_markup.inline_keyboard
    new_keyboard = []

    for row in old_keyboard:
        row_texts = [btn.text for btn in row]
        row_callbacks = [btn.callback_data for btn in row]

        # shu qatormi?
        if any(cb and cb.startswith(f"{bulletin_id}_") for cb in row_callbacks):
            # faqat tanlangan tugma qoladi
            if choice == VoteChoices.agree:
                new_row = [
                    InlineKeyboardButton("Roziman ✅", callback_data="noop")
                ]
            else:
                new_row = [
                    InlineKeyboardButton("Rozi emasman ❌", callback_data="noop")
                ]
            new_keyboard.append(new_row)
        else:
            # boshqa qatorlar o‘zgarmaydi
            new_keyboard.append(row)

    await query.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(new_keyboard)
    )
    full_name = await sync_to_async(get_user_full_name)(telegram_id)
    if full_name is None:
        full_name = f"{telegram_id} lik foydalanuvchi"
    await query.answer(f"{full_name.title()}, ovozingiz qabul qilindi ✅", show_alert=True)