from django.urls import path

from apps.employee.views import (EmployeeCreateAPIView, EmployeeListAPIView,
                                 EmployeeGetAPIView)

app_name = 'employee'

urlpatterns = [
    path('api/get-employee/', EmployeeGetAPIView.as_view(), name='get-employee'),
    path('list/', EmployeeListAPIView.as_view(), name='employee-list'),
    path('create/', EmployeeCreateAPIView.as_view(), name='employee-create'),
    # path('detail/<int:pk>', EmployeeRetrieveUpdateDestroyAPIView.as_view(), name='employee-crud')
]