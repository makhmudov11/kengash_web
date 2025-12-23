from django.urls import path

from apps.employee.views import (EmployeeListCreateAPIView, EmployeeListAPIView,
                                 EmployeeRetrieveUpdateDestroyAPIView)

app_name = 'employee'

urlpatterns = [
    path('list/', EmployeeListAPIView.as_view(), name='employee-list'),
    path('create/', EmployeeListCreateAPIView.as_view(), name='employee-create'),
    path('detail/<int:pk>', EmployeeRetrieveUpdateDestroyAPIView.as_view(), name='employee-crud')
]