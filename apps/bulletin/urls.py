from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.bulletin.views import (
    BulletinListView,
    BulletinCreateView,
    BulletinVoteCreateView,
    BulletinResultView, BulletinViewSet,
)

app_name = 'bulletin'

router = DefaultRouter()
router.register(r'bulletins', BulletinViewSet, basename='bulletin')

urlpatterns = [
    path('bulletins/', BulletinListView.as_view(), name='bulletin-list'),
    path('bulletins/create/', BulletinCreateView.as_view(), name='bulletin-create'),
    path('bulletins/vote/', BulletinVoteCreateView.as_view(), name='bulletin-vote'),
    path('bulletins/<int:pk>/result/', BulletinResultView.as_view(), name='bulletin-result'),

    path('', include(router.urls)),

]
