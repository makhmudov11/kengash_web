from django.utils import timezone
from rest_framework.generics import RetrieveUpdateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.users.choices import UserContactTypeChoices
from apps.users.models import SmsCodeTypeChoices, SmsCode
from apps.users.permissions import UserDetailPermission
from apps.users.serializers.user_detail import UserChangeRoleSerializer, UserDetailUpdateSerializer, \
    UserDetailRetrieveSerializer, UserDetailUpdateSendCodeSerializer
from apps.users.tasks import send_verification_code
from apps.utils import CustomResponse
from apps.utils.eskiz import EskizUZ
from apps.utils.generate_code import generate_code
from apps.utils.token_claim import get_tokens_for_user
from apps.utils.validates import validate_email_or_phone_number


class UserDetailUpdateAPIView(UpdateAPIView):
    serializer_class = UserDetailUpdateSerializer
    permission_classes = [UserDetailPermission]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        user = request.user
        contact = request.data.get('contact')

        if contact and contact != user.contact:
            sms_code_obj = SmsCode.objects.filter(
                contact=contact,
                _type=SmsCodeTypeChoices.UPDATE_CONTACT,
                delete_obj__gt=timezone.now(),
                verified=True
            ).order_by('-created_at').first()

            if not sms_code_obj:
                return CustomResponse.error_response(
                    message="Telefon raqam yoki email tasdiqlanmagan"
                )

        serializer = self.get_serializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return CustomResponse.success_response(
            message='Muvaffaqiyatli saqlandi',
            data=serializer.data
        )


class UserDetailUpdateSendCodeAPIView(APIView):
    serializer_class = UserDetailUpdateSendCodeSerializer
    permission_classes = [UserDetailPermission]

    def post(self, request):
        contact = request.data.get('contact', '').strip()
        if contact:
            contact_type = validate_email_or_phone_number(contact)
            if contact_type is False:
                return CustomResponse.error_response(
                    message="Telefon raqam yoki email kiritilishi mumkin."
                )
            code = generate_code()
            try:

                SmsCode.create_for_contact(contact=contact,
                                           code=code,
                                           _type=SmsCodeTypeChoices.UPDATE_CONTACT)
            except Exception as e:
                return CustomResponse.error_response(
                    message='Kod saqlashda xatolik'
                )
            if contact_type == UserContactTypeChoices.EMAIL:
                send_verification_code(email=contact, code=code)
            elif contact_type == UserContactTypeChoices.PHONE:
                phone = contact.lstrip('+')
                send_code = EskizUZ.send_sms_phone_number(phone_number=phone, code=code)
                if not send_code['success']:
                    return CustomResponse.error_response(
                        message=send_code['message'],
                        data=send_code['data']
                    )
            user = self.serializer_class(self.request.user).data
            return CustomResponse.success_response(
                message='Kod muvaffaqiyatli yuborildi',
                data=user
            )


class UserDetailRetrieveAPIView(RetrieveAPIView):
    serializer_class = UserDetailRetrieveSerializer
    permission_classes = [UserDetailPermission]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user


class UserSelectRoleRetrieveAPIView(APIView):
    permission_classes = [UserDetailPermission]

    def get(self, request):
        user = request.user
        return CustomResponse.success_response(
            data={
                "roles": user.roles,
                "active_role": request.auth["active_role"]
            }
        )


class UserChangeRoleAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserChangeRoleSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = serializer.validated_data.get('role')

        user = request.user
        if role not in getattr(user, 'roles', []):
            return CustomResponse.error_response(
                message=f"Userda {role} ro'li mavjud emas"
            )

        user.active_role = role
        user.save(update_fields=['active_role'])
        token = get_tokens_for_user(user)
        return CustomResponse.success_response(
            message="Role muvaffaqiyatli o'zgartirildi",
            data={
                "active_role": user.active_role,
                "token": token
            }
        )
