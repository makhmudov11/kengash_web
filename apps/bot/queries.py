from django.db.models import Q

from apps.bot.models import TelegramUser
from apps.bulletin.models import BulletinVote, BulletinGroup, Bulletin


def get_user_vote_count_in_group(group_id: int, user_tg_id: int) -> int:
    return BulletinVote.objects.select_related(
        'bulletin', 'bulletin__bulletin_group', 'telegram_user'
    ).filter(
        Q(telegram_user__telegram_id=user_tg_id) | Q(telegram_id=user_tg_id),
        bulletin__bulletin_group_id=group_id
    ).count()


def bulletin_group_in_bulletin_count(group_id: int):
    group = BulletinGroup.objects.get(id=group_id)
    count = group.bulletins.all().count()
    return count


def get_user(tg_id: int):
    data = TelegramUser.objects.select_related(
        'employee').filter(Q(telegram_id=tg_id) | Q(employee__tg_id=tg_id)).first()
    return data


def get_none_vote_bulletin(group_id: int, tg_id: int):
    bulletins = Bulletin.objects.filter(bulletin_group_id=group_id)
    bulletins = bulletins.exclude(votes__telegram_id=tg_id)
    return bulletins


def get_user_full_name(tg_id: int):
    user = TelegramUser.objects.filter(telegram_id=tg_id).first()
    if user and getattr(user, 'employee', None):
        return user.employee.full_name
    return None
