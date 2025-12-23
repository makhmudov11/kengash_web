from rest_framework.status import HTTP_201_CREATED

from apps.users.models import SmsCodeTypeChoices
from apps.users.serializers.user_detail import UserFullDataSerializer
from apps.utils import CustomResponse
from apps.utils.token_claim import get_tokens_for_user


class BaseVerifyCode:

    @classmethod
    def sms_code_type_response(cls, user_code_obj, user):
        if user_code_obj._type == SmsCodeTypeChoices.REGISTER:
            user.status = True
            user.save()
            user_data = UserFullDataSerializer(user).data
            user_code_obj.verified = True
            user_code_obj.save()
            return CustomResponse.success_response(
                message="Registratsiya muvaffqaiyatli bajarildi, foydalanuvchi yaratildi",
                data=user_data, code=HTTP_201_CREATED)
        elif user_code_obj._type == SmsCodeTypeChoices.CHANGE_PASSWORD:
            user_code_obj.verified = True
            user_code_obj.save()
            return CustomResponse.success_response(
                message="Parol o'zgartirish uchun kod tasdiqlandi",
                data={"user": user}
            )
        elif user_code_obj._type == SmsCodeTypeChoices.UPDATE_CONTACT:
            user_code_obj.verified = True
            user_code_obj.save()
            return CustomResponse.success_response(
                message='Kod tasdiqlandi'
            )
        else:
            user_code_obj.verified = True
            user_code_obj.save()
            token = get_tokens_for_user(user)
            user = UserFullDataSerializer(user).data
            return CustomResponse.success_response(
                message="Login muvaqqiyatli yakunlandi",
                data={"user": user, "token": token}
            )
