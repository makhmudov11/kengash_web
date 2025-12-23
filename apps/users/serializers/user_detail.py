from django.contrib.auth import get_user_model
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field

from rest_framework import serializers

from apps.users.choices import CustomUserRoleChoices
from apps.utils.CustomValidationError import CustomValidationError
from apps.utils.base_models import GenderChoices

User = get_user_model()

class UserFullDataSerializer(serializers.ModelSerializer):
    # last_login = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'full_name', 'contact', 'contact_type',
                  'active_role', 'image', 'birth_date', 'gender',
                  'status', 'last_login', 'is_active', 'is_staff', 'is_superuser',
                  'created_at', 'updated_at', 'deleted_at']

    # @extend_schema_field(serializers.CharField())
    # def get_last_login(self, obj):
    #     if obj.last_login:
    #         return (timezone.localtime(obj.last_login).strftime('%Y-%m-%d %H:%M:%S'))
    #     return None

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'contact', 'full_name', 'birth_date', 'image', 'created_at', 'active_role', 'status']


class UserDetailSerializer(serializers.ModelSerializer):
    image = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'contact', 'full_name', 'birth_date', 'image', 'created_at', 'active_role', 'status']
        extra_kwargs = {
            "id": {"read_only": True},
            "contact": {"read_only": True},
            "created_at": {"read_only": True},
            "active_role": {"read_only": True},
            "status": {"read_only": True},
        }


class UserDetailUpdateSerializer(serializers.ModelSerializer):
    image = serializers.FileField(required=False, allow_null=True)
    gender = serializers.ChoiceField(choices=GenderChoices.choices)

    class Meta:
        model = User
        fields = [ 'contact', 'full_name', 'birth_date', 'image', 'gender']

class UserDetailRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [ 'contact', 'full_name', 'birth_date', 'image', 'gender']

class UserSelectRoleSerializer(serializers.Serializer):
    role = serializers.JSONField(default=list)


class UserChangeRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=CustomUserRoleChoices.choices)

    if not role:
        raise CustomValidationError(detail=f"Ruxsat etilmagan role {role}")


class UserDetailUpdateSendCodeSerializer(serializers.Serializer):
    contact = serializers.CharField(max_length=255)