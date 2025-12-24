from django.urls import path
from .views import BulletinGroupCreateAPIView

app_name = 'bulletin'

urlpatterns = [
    path('api/bulletin-groups/create/', BulletinGroupCreateAPIView.as_view(), name='bulletin-group-create'),
]
