from django.http import Http404
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from apps.bot.bot import send_bulletin_to_group
from apps.bulletin.models import BulletinGroup, Bulletin
from apps.bulletin.serializers import BulletinGroupSerializer, BulletinListSerializer, BulletinSendLinkSerializer


class BulletinGroupCreateAPIView(CreateAPIView):
    queryset = BulletinGroup.objects.all()
    serializer_class = BulletinGroupSerializer
    permission_classes = [IsAuthenticated]


class BulletinListAPIView(ListAPIView):
    permissions = [IsAdminUser]
    serializer_class = BulletinListSerializer
    queryset = Bulletin.objects.all()


class SendBulletinGroup(ListAPIView):
    serializer_class = BulletinSendLinkSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        group_id = self.kwargs.get('group_id')
        if not group_id:
            raise Http404("Bulletin guruh id topilmadi")
        return Bulletin.objects.filter(bulletin_group_id=group_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        group_id = self.kwargs.get('group_id')
        bulletin_obj = BulletinGroup.objects.filter(id=group_id)
        print("SLAOLSJAHKJSAFHKSABKGABKGHABIHBAIGHAB", bulletin_obj)
        result = send_bulletin_to_group(bulletin_obj)  # Telegramga yuborish

        data = {
            "telegram_result": result,
            "bulletins": serializer.data
        }
        return Response(data)
#
#
# class BulletinGroupCreateAPIView(CreateAPIView):
#     serializer_class = BulletinGroupCreateSerializer
#     permission_classes = [AllowAny]
#     queryset = BulletinGroup.objects.all()
#
#
# class BulletinGroupDetailAPIView(RetrieveUpdateDestroyAPIView):
#     serializer_class = BulletinGroupDetailSerializer
#     permission_classes = [IsAdminUser]
#     queryset = BulletinGroup.objects.all()
#
#
# class BulletinGroupListAPIView(ListAPIView):
#     serializer_class = BulletinGroupListSerializer
#     permission_classes = [IsAdminUser]
#     queryset = BulletinGroup.objects.all()
#
#
#
# # 🔹 Bulletin ro'yxati (barchaga ochiq)
# class BulletinListView(generics.ListAPIView):
#     """Faol byulletenlar ro‘yxati"""
#     queryset = Bulletin.objects.order_by("-created_at")
#     serializer_class = BulletinSerializer
#     permission_classes = [permissions.IsAuthenticated]  # ✅ hamma ko‘ra oladi
#
#
# # 🔹 Faqat adminlar yaratadi
# class BulletinCreateView(generics.CreateAPIView):
#     queryset = Bulletin.objects.all()
#     serializer_class = BulletinSerializer
#     permission_classes = [permissions.IsAuthenticated]  # faqat login foydalanuvchi
#
#     def perform_create(self, serializer):
#         # Yaratuvchi foydalanuvchi avtomatik saqlanadi
#         serializer.save(created_by=self.request.user)
#
#
# # views.py
# class BulletinVoteCreateView(generics.CreateAPIView):
#     serializer_class = BulletinVoteSerializer
#     permission_classes = [permissions.AllowAny]
#
#     def perform_create(self, serializer):
#         telegram_id = serializer.validated_data.pop('telegram_id')
#         # bulletin = serializer.validated_data['bulletin']
#
#         tg_user = get_object_or_404(TelegramUser, telegram_id=telegram_id)
#
#         if not tg_user.is_verified:
#             raise serializers.ValidationError("Kontakt bazadan topilmadi!")
#
#         if not tg_user.employee:
#             raise serializers.ValidationError("Foydalanuvchi bog'lanmagan.")
#
#         serializer.save(telegram_user=tg_user)
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
#
#
# # 🔹 Byulleten natijalari (barchaga ochiq)
# class BulletinResultView(APIView):
#     """Bitta byulleten bo‘yicha natijalarni olish"""
#     permission_classes = [permissions.AllowAny]  # ✅ hamma ko‘ra oladi
#
#     def get(self, request, pk):
#         try:
#             bulletin = Bulletin.objects.get(pk=pk)
#         except Bulletin.DoesNotExist:
#             return Response({"detail": "Byulleten topilmadi."}, status=404)
#
#         data = {
#             "id": bulletin.id,
#             "full_name": bulletin.full_name,
#             "specialization": bulletin.specialization,
#             "title": bulletin.title,
#             "agree_count": bulletin.agree_count,
#             "disagree_count": bulletin.disagree_count,
#         }
#         return Response(data)
#
#
#
#
#
#
# from django.shortcuts import render
#
# # Create your views here.
