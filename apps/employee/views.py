import requests
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.views import APIView

from apps.employee.filters import AdminEmployeeListFilter
from apps.employee.models import Employee
from apps.employee.paginations import AdminUserEmployeeListPagination
from apps.employee.serializers import EmployeeListSerializer, EmployeeCreateSerializer, EmployeeUpdateSerializer, \
    EmployeeDetailGetSerializer, EmployeeGetSerializer


class EmployeeListAPIView(ListAPIView):
    serializer_class = EmployeeListSerializer
    permission_classes = [IsAdminUser]
    pagination_class = AdminUserEmployeeListPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = AdminEmployeeListFilter
    search_fields = ['department', 'full_name', 'lavozim', 'phone_number', 'tg_id', 'hemis_id']
    ordering_fields = ['created_at', 'updated_at', 'full_name']
    ordering = ['id']

    def get_queryset(self):
        queryset = Employee.objects.all()
        params = self.request.GET

        full_name = params.get("full_name")
        if full_name:
            queryset = queryset.filter(full_name__icontains=full_name)

        phone_number = params.get("phone_number")
        if phone_number:
            queryset = queryset.filter(phone_number__icontains=phone_number)

        tg_id = params.get("tg_id")
        if tg_id:
            queryset = queryset.filter(tg_id__icontains=tg_id)

        department = params.get("department")
        if department:
            queryset = queryset.filter(department__icontains=department)

        lavozim = params.get("lavozim")
        if lavozim:
            queryset = queryset.filter(lavozim__icontains=lavozim)

        return queryset


class EmployeeCreateAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Employee.objects.all()
    parser_classes = [FormParser, MultiPartParser]
    serializer_class = EmployeeCreateSerializer


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests


class EmployeeGetAPIView(APIView):
    serializer_class = EmployeeGetSerializer

    """
    Hemis API orqali xodimni hemis_id bo'yicha olish va faqat
    kerakli maydonlarni qaytarish: full_name, department, specialty, image_full
    """

    def get(self, request):
        hemis_id = request.query_params.get('hemis_id')  # GET parametri sifatida olish
        if not hemis_id:
            return Response({"success": False, "error": "hemis_id required"}, status=status.HTTP_400_BAD_REQUEST)

        url = f'https://student.tashmeduni.uz/rest/v1/data/employee-list?type=all&search={hemis_id}'
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        data = response.json()
        if not data.get("success"):
            return Response({"success": False, "error": "Hemis API returned failure"}, status=status.HTTP_404_NOT_FOUND)

        items = data.get("data", {}).get("items", [])
        if not items:
            return Response({"success": False, "error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)


        emp = items[0]
        result = {
            "full_name": emp.get("full_name"),
            "department": emp.get("department", {}).get("name"),
            "specialty": emp.get("specialty"),
            "image": emp.get("image") or emp.get("image")
        }

        return Response({"success": True, "data": result}, status=status.HTTP_200_OK)
