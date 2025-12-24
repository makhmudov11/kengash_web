from rest_framework import serializers

from apps.bulletin.models import Bulletin, BulletinVote


class BulletinSerializer(serializers.ModelSerializer):
    agree_count = serializers.IntegerField(read_only=True)
    disagree_count = serializers.IntegerField(read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Bulletin
        fields = [
            "id",
            "full_name",
            "specialization",
            "title",
            "agree_count",
            "disagree_count",
            "created_at",
            "created_by",
        ]


class BulletinVoteSerializer(serializers.ModelSerializer):
    telegram_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = BulletinVote
        fields = ['bulletin', 'choice', 'telegram_id']

    def validate(self, data):
        telegram_id = data.get('telegram_id')
        bulletin = data.get('bulletin')

        if BulletinVote.objects.filter(bulletin=bulletin, telegram_user__telegram_id=telegram_id).exists():
            raise serializers.ValidationError("Siz allaqachon ovoz bergansiz!")

        return data