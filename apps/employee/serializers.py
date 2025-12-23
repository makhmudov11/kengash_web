from rest_framework import serializers

from apps.employee.models import Employee


class EmployeeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


class EmployeeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['image', 'full_name', 'department', 'lavozim', 'phone_number', 'hemis_id']


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'image',
            'full_name',
            'department',
            'lavozim',
            'phone_number',
            'tg_id',
            'hemis_id'
        ]

class EmployeeDetailGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


class EmployeeGetSerializer(serializers.Serializer):
    hemis_id = serializers.CharField(max_length=50, required=True)