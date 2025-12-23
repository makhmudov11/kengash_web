from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAdminUser

from apps.employee.filters import AdminEmployeeListFilter
from apps.employee.models import Employee
from apps.employee.paginations import AdminUserEmployeeListPagination
from apps.employee.serializers import EmployeeListSerializer, EmployeeCreateSerializer, EmployeeUpdateSerializer, \
    EmployeeDetailGetSerializer


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
    permission_classes = [IsAdminUser]
    queryset = Employee.objects.all()
    parser_classes = [FormParser, MultiPartParser]
    serializer_class = EmployeeCreateSerializer


class EmployeeRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Employee.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return EmployeeUpdateSerializer
        return EmployeeDetailGetSerializer
