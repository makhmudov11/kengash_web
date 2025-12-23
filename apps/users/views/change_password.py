from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.users.choices import UserContactTypeChoices
from apps.users.models import SmsCode, SmsCodeTypeChoices
from apps.users.serializers.auth import UserForgotPasswordSerializer, UserResetPasswordSerializer
from apps.users.serializers.user_detail import UserFullDataSerializer
from apps.users.tasks import send_verification_code
from apps.utils import CustomResponse
from apps.utils.eskiz import EskizUZ
from apps.utils.generate_code import generate_code

User = get_user_model()


class UserForgotPasswordAPIView(APIView):
    serializer_class = UserForgotPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        contact = serializer.validated_data.get('contact')
        contact_type = serializer.validated_data['contact_type']

        user = User.objects.filter(contact=contact, status=True).first()

        if not user:
            return CustomResponse.error_response(message='User topilmadi')

        code = generate_code()
        try:
            SmsCode.create_for_contact(contact=contact, code=code, _type=SmsCodeTypeChoices.CHANGE_PASSWORD)
        except Exception as e:
            return CustomResponse.error_response(
                message='Kod yozishda xatolik'
            )

        try:
            if contact_type == UserContactTypeChoices.EMAIL:
                send_verification_code(email=contact, code=code)
            else:
                phone = contact.lstrip('+')
                send_code = EskizUZ.send_sms_phone_number(phone_number=phone, code=code)
                if not send_code['success']:
                    return CustomResponse.error_response(
                        message=send_code['message'],
                        data=send_code['data']
                    )
        except Exception as e:
            return CustomResponse.error_response(
                message='Kod yuborishda xatolik'
            )
        user = UserFullDataSerializer(user).data
        return CustomResponse.success_response(message='Parol tiklash uchun sms kod yuborildi.', data={"user": user})


class UserResetPasswordAPIView(APIView):
    serializer_class = UserResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        contact = request.data.get('contact', '').strip()
        password = request.data.get('password', '').strip()

        if not contact:
            return CustomResponse.error_response(message='Email yoki telefon raqam kelishi shart')

        if not password:
            return CustomResponse.error_response(message='Parol kiritilishi shart')

        user = User.objects.filter(contact=contact).first()
        if not user:
            return CustomResponse.error_response(message='User topilmadi')

        user_code_obj = SmsCode.objects.filter(
            contact=contact,
            expires_at__gte=timezone.now(),
            _type=SmsCodeTypeChoices.CHANGE_PASSWORD,
            verified=True
        ).order_by('-created_at').first()


        if not user_code_obj:
            return CustomResponse.error_response(message="Kod almashtirish imkoni yo'q")

        try:
            validate_password(password, user)
        except ValidationError as e:
            return CustomResponse.error_response(
                message="Parol talablariga javob bermaydi",
                data={
                    "errors": e.messages
                }
            )
        user.set_password(password)
        user.save(update_fields=['password'])
        user = UserFullDataSerializer(user).data
        return CustomResponse.success_response(message="Parol muvaffaqiyatli o'zgartirildi", data={"user": user})
