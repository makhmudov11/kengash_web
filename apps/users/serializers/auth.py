from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework.status import HTTP_400_BAD_REQUEST

from apps.users.choices import UserContactTypeChoices
from apps.utils.CustomValidationError import CustomValidationError
from apps.utils.validates import validate_email_or_phone_number

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    birth_date = serializers.DateField(
        input_formats=["%d.%m.%Y", "%d/%m/%Y"]
    )

    class Meta:
        model = User
        fields = ['id', 'full_name', 'contact', 'passport', 'birth_date', 'gender', 'password', 'status', 'created_at']
        extra_kwargs = {
            "password": {"write_only": True},
            "status": {"read_only": True},
            "created_at": {"read_only": True}
        }

    def validate(self, attrs):
        contact = attrs.get('contact', '').strip()
        full_name = attrs.get('full_name', '').strip()
        birth_date = attrs.get('birth_date', '')
        passport = attrs.get('passport', '').strip()
        gender = attrs.get('gender', '').strip()
        password = attrs.get('password', '').strip()

        if not full_name:
            raise CustomValidationError(detail="Ism va familiya kiritilishi shart.")

        if not birth_date:
            raise CustomValidationError(detail=" Tug'ilgan sana kiritilishi shart.")

        if not passport:
            raise CustomValidationError(detail="Passport seriya kiritilishi shart.")

        if not gender:
            raise CustomValidationError(detail="Passport seriya kiritilishi shart.")

        if not password:
            raise CustomValidationError(detail="Jins kiritilishi shart.")

        result = validate_email_or_phone_number(contact)

        if not result in [UserContactTypeChoices.EMAIL, UserContactTypeChoices.PHONE]:
            raise CustomValidationError(detail='Email yoki telefon raqam formati xato.')

        attrs['contact_type'] = result
        return attrs

    def create(self, validated_data):
        contact = validated_data.get('contact')
        user = User.objects.create(
            full_name=validated_data.get('full_name'),
            contact=contact,
            birth_date=validated_data.get('birth_date'),
            contact_type=validated_data.get('contact_type'),
            gender=validated_data.get('gender')
        )
        user.set_password(validated_data.get('password'))
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    contact = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100)

    def validate(self, attrs):
        contact = attrs.get('contact', '')
        password = attrs.get('password', '')

        if not contact:
            raise CustomValidationError(detail="Email yoki telefon raqam kiritilishi shart.")

        if not password:
            raise CustomValidationError(detail="Parol kiritilishi shart.")

        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=255)

    def validate(self, attrs):
        token = attrs.get('refresh_token', '').strip()
        if not token:
            raise CustomValidationError(detail='Token kelishi shart', code=HTTP_400_BAD_REQUEST)
        return attrs


class UserForgotPasswordSerializer(serializers.Serializer):
    contact = serializers.CharField(max_length=100)

    def validate(self, attrs):
        contact = attrs.get('contact', '').strip()

        if not contact:
            raise CustomValidationError(detail='Email yoki telefon raqam kelishi shart')

        contact_type = validate_email_or_phone_number(contact)

        if contact_type not in [UserContactTypeChoices.EMAIL, UserContactTypeChoices.PHONE]:
            raise CustomValidationError(detail='Email yoki telefon formati xato.')

        attrs['contact_type'] = contact_type
        return attrs


class UserResetPasswordSerializer(serializers.Serializer):
    contact = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100)
