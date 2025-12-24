from django.urls import path

from apps.bot.views import VerifyContactView, publish_bulletin, BulletinVoteCreateView

urlpatterns = [
    path('bulletins/<int:bulletin_id>/publish/', publish_bulletin, name='publish_bulletin'),
    path('verify-contact/', VerifyContactView.as_view(), name='verify-contact'),
    path('bulletins/vote/', BulletinVoteCreateView.as_view(), name='bulitn-vote'),


]
