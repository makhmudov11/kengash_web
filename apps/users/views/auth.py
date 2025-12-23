from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import SmsCodeTypeChoices, UserContactTypeChoices, SmsCode
from apps.users.serializers.auth import RegisterSerializer, LoginSerializer, LogoutSerializer
from apps.users.serializers.user_detail import UserFullDataSerializer

from apps.users.tasks import send_verification_code
from apps.utils import CustomResponse
from apps.utils.eskiz import EskizUZ
from apps.utils.generate_code import generate_code
from apps.utils.validates import validate_email_or_phone_number

User = get_user_model()


class RegisterCreateAPIView(CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        contact = request.data.get('contact', '').strip()
        if not contact:
            return CustomResponse.error_response(
                message="Email yoki telefon raqam kiritilishi shart",
                code=status.HTTP_400_BAD_REQUEST
            )
        if User.objects.filter(contact=contact, status=True).exists():
            return CustomResponse.error_response(
                message=f"{contact} orqali avval ro'yhatdan o'tilgan"
            )
        User.objects.filter(contact=contact, status=False).delete()
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact_type = serializer.validated_data.get('contact_type')

        code = generate_code()
        try:
            SmsCode.create_for_contact(
                contact=contact,
                code=code,
                _type=SmsCodeTypeChoices.REGISTER
            )
        except Exception as e:
            return CustomResponse.error_response(message='Kod saqlashda xatolik.')
        user = serializer.save()
        user = UserFullDataSerializer(user).data


        if contact_type == UserContactTypeChoices.EMAIL:
            try:
                send_verification_code(email=contact, code=code)
            except Exception as e:
                return CustomResponse.error_response(
                    message='Kod yuborishda xatolik'
                )

        else:
            phone = contact.lstrip('+')
            send_code = EskizUZ.send_sms_phone_number(phone_number=phone, code=code)
            if not send_code['success']:
                return CustomResponse.error_response(
                    message=send_code['message'],
                    data=send_code['data']
                )
        return CustomResponse.success_response(
            message='Kod muvaffaqiyatli yuborildi',
            data=user
        )


class LoginAPIView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = serializer.validated_data.get('contact').strip()
        password = serializer.validated_data.get('password').strip()

        try:
            user = User.objects.get(contact=contact, status=True)
        except User.DoesNotExist:
            return CustomResponse.error_response(message="User topilmadi", code=HTTP_404_NOT_FOUND)

        if not user.check_password(password):
            return CustomResponse.error_response(message="Parol noto'g'ri", code=HTTP_401_UNAUTHORIZED)

        code = generate_code()
        try:

            SmsCode.create_for_contact(contact=contact,
                                       code=code,
                                       _type=SmsCodeTypeChoices.LOGIN)
        except Exception as e:
            return CustomResponse.error_response(
                message='Kod saqlashda xatolik'
            )

        contact_type = validate_email_or_phone_number(contact)

        if contact_type == UserContactTypeChoices.EMAIL:
            try:
                send_verification_code(email=contact, code=code)
            except Exception as e:
                return CustomResponse.error_response(
                    message='Kod yuborishda xatolik yuz berdi.'
                )
        else:
            phone = contact.lstrip('+')
            send_code = EskizUZ.send_sms_phone_number(phone_number=phone, code=code)
            if not send_code['success']:
                return CustomResponse.error_response(
                    message=send_code['message'],
                    data=send_code['data']
                )
        user = UserFullDataSerializer(user).data
        return CustomResponse.success_response(
            message='Kod muvaffaqiyatli yuborildi',
            data=user
        )


class UserLogoutAPIView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data.get('refresh_token').split()
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return CustomResponse.success_response(
                message='Chiqish muvaffaqiyatli bajarildi'
            )
        except TokenError:
            return CustomResponse.error_response(
                message='Refresh token yaroqsiz',
                code=HTTP_400_BAD_REQUEST
            )
