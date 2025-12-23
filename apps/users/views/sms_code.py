from datetime import timedelta

from attr.setters import validate
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.views import APIView

from apps.users.choices import UserContactTypeChoices
from apps.users.models import SmsCode
from apps.users.serializers.sms_code import SmsCodeSerializer, ResendCodeSerializer, VerifyCodeSerializer
from apps.users.tasks import send_verification_code
from apps.utils import CustomResponse
from apps.utils.eskiz import EskizUZ
from apps.utils.generate_code import generate_code
from apps.utils.validates import validate_email_or_phone_number

User = get_user_model()


class VerifyCodeAPIView(APIView):
    serializer_class = VerifyCodeSerializer
    MAX_ATTEMPTS = 3

    def post(self, request):
        contact = request.data.get('contact', '').strip()
        if not contact:
            return CustomResponse.error_response(message='Email yoki telefon raqam kelishi shart')

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data.get('code')

        user = User.objects.filter(contact=contact).first()
        if not user:
            return CustomResponse.error_response(message='User topilmadi')

        user_code_obj = SmsCode.objects.filter(
            contact=contact,
            verified=False,
            expires_at__gte=timezone.now()
        ).order_by('-created_at').first()

        if not user_code_obj:
            return CustomResponse.error_response(message="Kod topilmadi")

        if code != user_code_obj.send_code:
            user_code_obj.attempts += 1
            user_code_obj.save()

            if user_code_obj.attempts == self.MAX_ATTEMPTS:
                return CustomResponse.error_response(message="Urinishlar soni tugadi.")

            return CustomResponse.error_response(
                message=f"Kod noto'g'ri kiritildi.",
                data={
                    "sms_code_obj": SmsCodeSerializer(user_code_obj).data,
                    "attempts": self.MAX_ATTEMPTS - user_code_obj.attempts
                },
            )
        from apps.utils.BaseClass import BaseVerifyCode
        BaseVerifyCode.sms_code_type_response(user_code_obj, user)


class ResendCode(APIView):
    serializer_class = ResendCodeSerializer

    MAX_RESEND_CODE = 3

    def post(self, request):
        contact = request.data.get('contact', '').strip()

        if not contact:
            return CustomResponse.error_response(message="Email yoki telefon raqam kelishi shart.")

        user_code_obj = SmsCode.objects.filter(
            contact=contact,
            verified=False,
            delete_obj__gte=timezone.now()
        ).order_by('-created_at').first()

        if not user_code_obj:
            return CustomResponse.error_response(message='Kod topilmadi.')

        if user_code_obj.resend_code >= self.MAX_RESEND_CODE:
            return CustomResponse.error_response(
                message="Urinishlar soni tugadi.",
                data=SmsCodeSerializer(user_code_obj).data
            )

        code = generate_code()
        user_code_obj.resend_code += 1
        user_code_obj.expires_at = timezone.now() + timedelta(seconds=180)
        user_code_obj.attempts = 0
        user_code_obj.send_code = code
        user_code_obj.save()
        contact_type = validate_email_or_phone_number(contact)
        try:
            if contact_type == UserContactTypeChoices.EMAIL:
                send_verification_code(contact, code)
            elif contact_type == UserContactTypeChoices.PHONE:
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
        sms_code_obj = SmsCodeSerializer(user_code_obj).data
        return CustomResponse.success_response(
            data={
                "contact": contact,
                "sms_code_obj": sms_code_obj,
                "qayta_jonatish_qoldi": self.MAX_RESEND_CODE - sms_code_obj['resend_code']
            },
            message="Kod qaytadan yuborildi."
        )
