from django.urls import path

from apps.face.views import EmployeeFaceAttendanceAPIView

app_name = 'face'

urlpatterns = [
    path('attendance/employee/', EmployeeFaceAttendanceAPIView.as_view(), name='attendance-employee'),
]