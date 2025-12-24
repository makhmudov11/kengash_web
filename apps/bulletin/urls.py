from django.urls import path
from .views import BulletinGroupCreateAPIView, BulletinListAPIView

app_name = 'bulletin'

urlpatterns = [
    path('groups/create/', BulletinGroupCreateAPIView.as_view(), name='bulletin-group-create'),
    path('list/', BulletinListAPIView.as_view(), name='bulletin-list'),
]
