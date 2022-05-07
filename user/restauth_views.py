from dj_rest_auth import views as dj_rest_auth_views
from dj_rest_auth.app_settings import create_token
from dj_rest_auth.models import TokenModel
from dj_rest_auth.serializers import JWTSerializer, TokenSerializer
from dj_rest_auth.utils import jwt_encode
from django.contrib.auth import login
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from vortex_task import settings
from .permissions import IsGuest as IsGuestPermission
from . import serializers


class IsGuest(APIView):
    def get_permissions(self):
        permissions_list = super().get_permissions()
        permissions_list.append(IsGuestPermission())
        return permissions_list


class PasswordResetView(IsGuest, dj_rest_auth_views.PasswordResetView):
    pass


class PasswordResetConfirmView(IsGuest, dj_rest_auth_views.PasswordResetConfirmView):
    pass


class LoginView(IsGuest, dj_rest_auth_views.LoginView):
    serializer_class = serializers.LoginSerializer


sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters('password1', 'password2'),
)


class RegisterView(IsGuest, CreateAPIView):
    serializer_class = serializers.RegisterSerializer
    permission_classes = (AllowAny,)
    token_model = TokenModel
    throttle_scope = 'dj_rest_auth'

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_response_data(self, user):
        if getattr(settings, 'REST_USE_JWT', False):
            data = {
                'user': user,
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
            }
            return JWTSerializer(data, context=self.get_serializer_context()).data
        elif getattr(settings, 'REST_SESSION_LOGIN', False):
            return None
        else:
            return TokenSerializer(user.auth_token, context=self.get_serializer_context()).data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = self.get_response_data(user)

        if data:
            response = Response(
                data,
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        else:
            response = Response(status=status.HTTP_204_NO_CONTENT, headers=headers)

        return response

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        if getattr(settings, 'REST_USE_JWT', False):
            self.access_token, self.refresh_token = jwt_encode(user)
        elif not getattr(settings, 'REST_SESSION_LOGIN', False):
            # Session authentication isn't active either, so this has to be
            #  token authentication
            create_token(self.token_model, user, serializer)

        login(self.request, user)
        return user

