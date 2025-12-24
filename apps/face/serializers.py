from rest_framework import serializers

from apps.employee.serializers import EmployeeCreateSerializer
from apps.face.models import Attendance


class EmployeeFaceAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'


class EmployeeFaceAttendanceListSerializer(serializers.ModelSerializer):
    employee = EmployeeCreateSerializer()
    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'status', 'arrival_time']