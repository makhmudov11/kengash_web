from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from apps.users.serializers import LoginSerializer
from apps.utils.token_claim import get_tokens_for_user

from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from apps.users.serializers import LoginSerializer
from apps.utils.token_claim import get_tokens_for_user


class LoginAPIView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {
                    "success": False,
                    "message": "Username yoki parol noto‘g‘ri"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        token = get_tokens_for_user(user)

        return Response(
            {
                "success": True,
                "message": "Login muvaffaqiyatli",
                "token": token
            },
            status=status.HTTP_200_OK
        )
