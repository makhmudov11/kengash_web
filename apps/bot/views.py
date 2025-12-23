from rest_framework import generics, permissions, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, AllowAny
from django.views.decorators.csrf import csrf_exempt

from .bot import send_bulletin_to_group
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import TelegramUser
from ..bulletin.models import Bulletin
from ..employee.models import Employee


@csrf_exempt  # CSRF xatosiz ishlashi uchun
@api_view(['POST'])
@permission_classes([IsAdminUser])
def publish_bulletin(request, bulletin_id):
    bulletin = get_object_or_404(Bulletin, id=bulletin_id)
    res = send_bulletin_to_group(bulletin)
    return Response(res)


class VerifyContactView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        tg_id = request.data.get('tg_id')
        phone_number = request.data.get('phone_number')


        if not all([tg_id, phone_number]):
            return Response({"message": "Telegram ID va telefon kerak"}, status=400)

        phone_suffix = phone_number[-9:]  # 901234567

        employee = Employee.objects.filter(
            phone_number__endswith=phone_suffix
        ).first()

        if not employee:
            return Response({
                "allowed": False,
                "message": "Telefon raqam ro'yxatda yo'q."
            }, status=403)

        tg_user, created = TelegramUser.objects.get_or_create(
            telegram_id=tg_id,
            defaults={'employee': employee}
        )

        if not created and tg_user.employee != employee:
            return Response({
                "allowed": False,
                "message": "Bu Telegram ID boshqa odamga bog'langan."
            }, status=403)

        return Response({
            "allowed": True,
            "employee_name": employee.full_name,
            "message": "Kontakt tasdiqlandi. Ovoz bering."
        }, status=200)


