from rest_framework import serializers

from apps.face.models import Attendance


class EmployeeFaceAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'