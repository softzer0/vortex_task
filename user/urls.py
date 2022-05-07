from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from dj_rest_auth.views import LogoutView
from rest_framework.urlpatterns import format_suffix_patterns
from .restauth_views import *
from .views import *

urlpatterns = format_suffix_patterns([
    # URLs that do not require a session or valid token
    path('password/reset/', PasswordResetView.as_view(),
         name='rest_password_reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(),
         name='rest_password_reset_confirm'),
    path('login/', LoginView.as_view(), name='rest_login'),
    path('register/', RegisterView.as_view(), name='rest_register'),

    # URLs that require a user to be logged in with a valid session / token.
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='rest_logout'),

    path('user/', UserDetailsView.as_view(), name='user_details')
])
