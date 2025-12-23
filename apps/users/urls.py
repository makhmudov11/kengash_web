
from django.urls import path


from apps.users.views.auth import RegisterCreateAPIView, LoginAPIView, UserLogoutAPIView
from apps.users.views.change_password import UserForgotPasswordAPIView, UserResetPasswordAPIView
from apps.users.views.detail import UserSelectRoleRetrieveAPIView, UserDetailRetrieveAPIView, \
    UserDetailUpdateAPIView, UserChangeRoleAPIView, UserDetailUpdateSendCodeAPIView
from apps.users.views.sms_code import VerifyCodeAPIView, ResendCode

app_name = 'users'

urlpatterns = [
    path('register/', RegisterCreateAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('verify-code/', VerifyCodeAPIView.as_view(), name='verify'),
    path('forgot-password/', UserForgotPasswordAPIView.as_view(), name='forgot-password'),
    path('reset-password/', UserResetPasswordAPIView.as_view(), name='reset-password'),
    path('logout/', UserLogoutAPIView.as_view(), name='reset-password'),
    # path('auth/social/google/', UserGoogleSocialAuthAPIView.as_view(), name='auth-social-google'),
    # path('auth/social/facebook/', UserFacebookSocialAuthAPIView.as_view(), name='auth-social-facebook'),
    # path('auth/social/apple/', UserAppleSocialAuthAPIView.as_view(), name='auth-social-apple'),
    # path('resend-code/', ResendCode.as_view(), name='resend-code'),
    path('info/detail/', UserDetailRetrieveAPIView.as_view(), name='user-detail'),
    path('info/detail/update', UserDetailUpdateAPIView.as_view(), name='user-detail'),
    path('detail/update/contact/send-code', UserDetailUpdateSendCodeAPIView.as_view(), name='update-contact-send-code'),
    path('select-roles/', UserSelectRoleRetrieveAPIView.as_view(), name='select-roles'),
    path('change-role/', UserChangeRoleAPIView.as_view(), name='change-role'),

]
