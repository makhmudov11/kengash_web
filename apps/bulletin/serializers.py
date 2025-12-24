from rest_framework import serializers
from .models import BulletinGroup, Bulletin


class BulletinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bulletin
        fields = ['id', 'full_name', 'specialization', 'title']


class BulletinGroupSerializer(serializers.ModelSerializer):
    bulletins = BulletinSerializer(many=True)

    class Meta:
        model = BulletinGroup
        fields = ['id', 'name', 'bulletins']

    def create(self, validated_data):
        bulletins_data = validated_data.pop('bulletins', [])
        user = self.context['request'].user
        if user.is_anonymous:
            raise serializers.ValidationError("Login qilgan foydalanuvchi kerak")

        group = BulletinGroup.objects.create(created_by=user, **validated_data)
        for bulletin_data in bulletins_data:
            Bulletin.objects.create(bulletin_group=group, **bulletin_data)
        return group


class BulletinLIstSerializer(serializers.ModelSerializer):
    bulletin_group = BulletinGroupSerializer()

    def get_attendance_agree(self, obj):

    class Meta:
        model = Bulletin
        fields = ['id', 'full_name', 'bulletin_group', 'specialization', 'title']

# from rest_framework import serializers
#
# from apps.bulletin.models import Bulletin, BulletinVote, BulletinGroup
#
#
# class BulletinSerializer(serializers.ModelSerializer):
#     agree_count = serializers.IntegerField(read_only=True)
#     disagree_count = serializers.IntegerField(read_only=True)
#     created_by = serializers.StringRelatedField(read_only=True)  # foydalanuvchi nomi faqat ko‘rsatish uchun
#
#     class Meta:
#         model = Bulletin
#         fields = [
#             "id",
#             "full_name",
#             "specialization",
#             "title",
#             "agree_count",
#             "disagree_count",
#             "created_at",
#             "created_by",
#         ]
#
#
# # serializers.py
# class BulletinVoteSerializer(serializers.ModelSerializer):
#     telegram_id = serializers.IntegerField(write_only=True)
#
#     class Meta:
#         model = BulletinVote
#         fields = ['bulletin', 'choice', 'telegram_id']
#
#     def validate(self, data):
#         telegram_id = data.get('telegram_id')
#         bulletin = data.get('bulletin')
#
#         if BulletinVote.objects.filter(bulletin=bulletin, telegram_user__telegram_id=telegram_id).exists():
#             raise serializers.ValidationError("Siz allaqachon ovoz bergansiz!")
#
#         if bulletin.status:
#             pass
#         else:
#             raise serializers.ValidationError("Ovoz berish yakunlangan!")
#
#         return data
#
# class BulletinGroupCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BulletinGroup
#         fields = ['id', 'name', 'status']
#         extra_kwargs = {'name': {'write_only': True}}
#
# class BulletinGroupDetailSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BulletinGroup
#         fields = ['id', 'name', 'status']
#         read_only_fields = ['id']
#
# class BulletinGroupListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BulletinGroup
#         fields = '__all__'
