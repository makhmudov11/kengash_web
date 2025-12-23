from django.urls import path

from apps.employee.views import (EmployeeCreateAPIView, EmployeeListAPIView,
                                 EmployeeRetrieveUpdateDestroyAPIView)

app_name = 'employee'

urlpatterns = [
    path('list/', EmployeeListAPIView.as_view(), name='employee-list'),
    path('create/', EmployeeCreateAPIView.as_view(), name='employee-create'),
    path('detail/<int:pk>', EmployeeRetrieveUpdateDestroyAPIView.as_view(), name='employee-crud')
]