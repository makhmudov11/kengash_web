
from rest_framework import serializers

from apps.users.models import SmsCode
from apps.utils.CustomValidationError import CustomValidationError


class SmsCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmsCode
        fields = ['id', 'contact', 'attempts', 'resend_code', 'verified',
                  'expires_at', 'delete_obj', '_type', 'created_at']


class VerifyCodeSerializer(serializers.Serializer):
    contact = serializers.CharField(max_length=200)
    code = serializers.CharField(max_length=100)

    def validate(self, attrs):
        code = attrs.get('code', '').strip()
        if len(code) != 6:
            raise CustomValidationError(detail="Parol uzunligi 6 ta bo'lishi kerak")
        return attrs


class ResendCodeSerializer(serializers.Serializer):
    contact = serializers.CharField(max_length=200, required=True)

