from asgiref.sync import sync_to_async
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from apps.bot.queries import bulletin_group_in_bulletin_count, get_user_vote_count_in_group, get_none_vote_bulletin, \
    get_user_full_name
from apps.bulletin.models import BulletinGroup, VoteChoices


def get_contact_keyboard():
    keyboard = [[KeyboardButton("Kontakt yuborish", request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


async def send_voting_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE, group_id: int, user_tg_id: int):
    bulletins_count = await sync_to_async(bulletin_group_in_bulletin_count)(group_id)

    if not bulletins_count:
        await update.message.reply_text(
            "Hozircha bu guruhda ovoz berish uchun xodimlar yo‘q."
        )
        return

    user_votes_count = await sync_to_async(get_user_vote_count_in_group)(group_id, user_tg_id)

    if user_votes_count == bulletins_count:
        await update.message.reply_text(
            "Barcha bulletinlar uchun ovoz bergansiz.",
            reply_markup=None
        )
        return

    data_no_votes = await sync_to_async(get_none_vote_bulletin)(group_id, user_tg_id)

    bulletin_group = await sync_to_async(BulletinGroup.objects.get)(
        id=group_id
    )
    if not bulletin_group.status:
        await update.message.reply_text(
            "Ovoz berish tugagan."
        )
        return
    #
    keyboards = []
    for bulletin in data_no_votes:
        if bulletin.full_name:
            keyboards.append(
                [InlineKeyboardButton(bulletin.full_name.title(), callback_data="noop")]
            )
            keyboards.append(
                [
                    InlineKeyboardButton('Roziman ✅',
                                         callback_data=f'{bulletin.pk}_{VoteChoices.agree}'),
                    InlineKeyboardButton('Rozi emasman ❌',
                                         callback_data=f'{bulletin.pk}_{VoteChoices.disagree}')
                ]
            )
    keyboards.append(
        [InlineKeyboardButton('Tasdiqlash', callback_data='submit')]
    )
    reply_markup = InlineKeyboardMarkup(keyboards)
    user = await sync_to_async(get_user_full_name)(user_tg_id)
    if user is None:
        full_name = f"{user_tg_id} lik user"
    else:
        full_name = user
    await update.message.reply_text(
        f"{full_name.title()}, nomzodlarga ovoz bering:",
        reply_markup=reply_markup
    )
    return
