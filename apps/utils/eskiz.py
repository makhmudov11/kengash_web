import decouple
import requests
from django.core.cache import cache

from apps.users.models import SmsCodeTypeChoices
from apps.utils.CustomValidationError import CustomValidationError


class EskizUZ:
    _TOKEN_KEY = "eskiz_access_token"

    GET_TOKEN_URL = "https://notify.eskiz.uz/api/auth/login"
    SEND_SMS_URL = "https://notify.eskiz.uz/api/message/sms/send"

    _AUTH_CODE_MESSAGE = "Tasdiqlash kodingiz: {code}"
    _FORGOT_PASSWORD_MESSAGE = "Parolni tiklash kodingiz: {code}"

    _ESKIZ_EMAIL = decouple.config("ESKIZ_EMAIL")
    _ESKIZ_PASSWORD = decouple.config("ESKIZ_PASSWORD")

    @classmethod
    def get_token(cls):
        token = cache.get(cls._TOKEN_KEY, '')
        if not token:
            try:
                response = requests.post(
                    url=cls.GET_TOKEN_URL,
                    data={
                        "email": cls._ESKIZ_EMAIL,
                        "password": cls._ESKIZ_PASSWORD
                    }
                )
                response.raise_for_status()
                token = response.json()['data']['token']

                cache.set(cls._TOKEN_KEY, token, timeout=60 * 60 * 23)
            except Exception as e:
                raise CustomValidationError(
                    detail="Token olishda xatolik"
                )
        return token

    @classmethod
    def send_sms_phone_number(cls, phone_number, code, message_type=None, nickname='4546'):
        timeout = 10
        if message_type == SmsCodeTypeChoices.CHANGE_PASSWORD:
            message = cls._FORGOT_PASSWORD_MESSAGE
        else:
            message = cls._AUTH_CODE_MESSAGE
        message = message.format(code=code)

        headers = {
            "Authorization": f"Bearer {cls.get_token()}"
        }
        data = {
            "mobile_phone": phone_number,
            "message": message,
            "from": nickname
        }
        response = requests.post(
            url=cls.SEND_SMS_URL,
            headers=headers,
            data=data
        )
        if response.status_code == 401:
            cache.delete(cls._TOKEN_KEY)
            headers["Authorization"] = f"Bearer {cls.get_token()}"
            response = requests.post(
                cls.SEND_SMS_URL,
                headers=headers,
                data=data,
                timeout=timeout
            )

        try:
            response_data = response.json()
        except ValueError:
            response_data = {
                "message": response.text or "Eskiz API JSON qaytarmadi"
            }

        if response.status_code in (200, 201):
            return {
                "success": True,
                "status_code": response.status_code,
                "message": response_data.get("message", "SMS yuborildi"),
                "data": response_data
            }

        return {
            "success": False,
            "status_code": response.status_code,
            "message": response_data.get("message", "Eskiz API xatosi"),
            "data": response_data
        }