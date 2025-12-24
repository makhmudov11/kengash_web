from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.employee.models import Employee
from apps.face.models import Attendance, AttendanceChoice
from apps.face.serializers import EmployeeFaceAttendanceSerializer, EmployeeFaceAttendanceListSerializer

from django.utils.dateparse import parse_datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class EmployeeFaceAttendanceAPIView(APIView):

    def post(self, request):
        date_time_str = request.data.get('dateTime')
        arrival_time = parse_datetime(date_time_str)

        if not arrival_time:
            return Response(
                {"error": "DateTime noto‘g‘ri"},
                status=status.HTTP_400_BAD_REQUEST
            )

        event_data = request.data.get('AccessControllerEvent')
        if not isinstance(event_data, dict):
            return Response(
                {"error": "AccessControllerEvent noto‘g‘ri"},
                status=status.HTTP_400_BAD_REQUEST
            )

        hemis_id = event_data.get('employeeNoString')
        if not hemis_id:
            return Response(
                {"error": "Hemis id  topilmadi"},
                status=status.HTTP_400_BAD_REQUEST
            )

        employee = Employee.objects.filter(hemis_id=hemis_id).first()
        if not employee:
            return Response(
                {"error": f"{hemis_id} bo‘yicha employee topilmadi"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            attendance = Attendance.objects.create(
                employee=employee,
                status=AttendanceChoice.KELDI,
                arrival_time=arrival_time
            )
        except Exception as e:
            return Response(
                {"error": "Ma'lumot saqlashda xatolik"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            EmployeeFaceAttendanceSerializer(attendance).data,
            status=status.HTTP_201_CREATED
        )

class EmployeeFaceAttendanceListAPIView(ListAPIView):
    serializer_class = EmployeeFaceAttendanceListSerializer
    permission_classes = [IsAdminUser]
    queryset = Attendance.objects.select_related('employee')