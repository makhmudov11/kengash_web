from django.contrib.auth.models import User
from django.db import models
from rest_framework.exceptions import ValidationError

from apps.bot.models import TelegramUser


class BulletinGroup(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.name or self.pk

    def clean(self):
        if BulletinGroup.objects.filter(
                name=self.name
        ).exclude(pk=self.pk).exists():
            raise ValidationError(f'{self.name} nomli guruh avval yratilgan')


class Bulletin(models.Model):
    bulletin_group = models.ForeignKey(BulletinGroup, on_delete=models.CASCADE,
                                       related_name='bulletins')
    full_name = models.CharField(max_length=255)
    specialization = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, default="Professor")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} - {self.title}"

    @property
    def agree_count(self):
        return self.votes.filter(choice='agree').count()

    @property
    def disagree_count(self):
        return self.votes.filter(choice='disagree').count()


class VoteChoices(models.TextChoices):
    agree = 'agree', 'Agree'
    disagree = 'disagree', 'Disagree'


class BulletinVote(models.Model):
    bulletin = models.ForeignKey(Bulletin, on_delete=models.CASCADE, related_name='votes')

    telegram_user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name='tg_users',
        null=True,
        blank=True
    )
    telegram_id = models.PositiveBigIntegerField(null=True, blank=True)
    choice = models.CharField(max_length=10, choices=VoteChoices.choices)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('bulletin', 'telegram_user', 'telegram_id')

    def __str__(self):
        tg = self.telegram_user.telegram_id if self.telegram_user else self.telegram_id
        return f"{tg} → {self.bulletin} ({self.choice})"

    def clean(self):
        if BulletinVote.objects.filter(
            bulletin=self.bulletin,
            telegram_user=self.telegram_user
        ).exists():
            raise ValidationError('Siz avval ovoz bergansiz ')

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.telegram_user and not self.telegram_id:
            self.telegram_id = self.telegram_user.telegram_id
        super().save(*args, **kwargs)