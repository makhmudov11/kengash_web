from django.urls import path

from apps.users.views import  LoginAPIView

app_name = "users"

urlpatterns = [
    path('', LoginAPIView.as_view())
]