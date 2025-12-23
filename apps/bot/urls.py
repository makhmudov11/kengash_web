from django.urls import path

from bot.views import publish_bulletin, VerifyContactView

urlpatterns = [
    path('bulletins/<int:bulletin_id>/publish/', publish_bulletin, name='publish_bulletin'),
    path('verify-contact/', VerifyContactView.as_view(), name='verify-contact'),


]
