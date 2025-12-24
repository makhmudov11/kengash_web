from django.urls import path

from apps.face.views import EmployeeFaceAttendanceAPIView, EmployeeFaceAttendanceListAPIView, TodayAttendanceListAPIView

app_name = 'face'

urlpatterns = [
    path('attendance/employee/', EmployeeFaceAttendanceAPIView.as_view(), name='attendance-employee'),
    path('attendance/list/', EmployeeFaceAttendanceListAPIView.as_view(), name='attendance-list'),
    path('today/attendance/list/', TodayAttendanceListAPIView.as_view(), name='today-attendance-list'),
]