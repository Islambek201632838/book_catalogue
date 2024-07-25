from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import *


urlpatterns = [
    path('auth/', include('djoser.urls')),  # Include Djoser default URLs
    path('auth/', include('djoser.urls.jwt')),  # Include Djoser JWT URLs
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='auth_logout'),
    path('auth/login/', LoginView.as_view(), name='auth_login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('auth/send-reset-code/', SendResetCodeView.as_view(), name='send_reset_code'),
    path('auth/verify-reset-code/', VerifyResetCodeView.as_view(), name='verify_reset_code'),
    path('auth/reset-password-with-code/', ResetPasswordWithCodeView.as_view(), name='reset_password_with_code'),
]
