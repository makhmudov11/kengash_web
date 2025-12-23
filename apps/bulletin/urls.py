from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.bulletin.views import (
    BulletinListView,
    BulletinCreateView,
    BulletinVoteCreateView,
    BulletinResultView, BulletinGroupCreateAPIView, BulletinGroupDetailAPIView, BulletinGroupListAPIView,
)

app_name = 'bulletin'



urlpatterns = [
    path('bulletins/', BulletinListView.as_view(), name='bulletin-list'),
    path('bulletins/create/', BulletinCreateView.as_view(), name='bulletin-create'),
    path('bulletins/vote/', BulletinVoteCreateView.as_view(), name='bulletin-vote'),
    path('bulletins/<int:pk>/result/', BulletinResultView.as_view(), name='bulletin-result'),
    path('bulletin-group/create/', BulletinGroupCreateAPIView.as_view(), name='bulletin-group-create'),
    path('bulletin-group/detail/<int:pk>', BulletinGroupDetailAPIView.as_view(), name='bulletin-group-detail'),
    path('bulletin-group/list', BulletinGroupListAPIView.as_view(), name='bulletin-group-list'),

    path('', include(router.urls)),

]
