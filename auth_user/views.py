from djoser.compat import get_user_email
from djoser.views import UserViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from catalogue_app.settings import CACHE_TIMEOUT
from .serializers import UserProfileSerializer, ResetPasswordWithCodeSerializer
from rest_framework.decorators import action
from djoser import signals
from djoser.conf import settings as djoser_settings
from djoser.utils import decode_uid
from django.utils.translation import gettext as _
from django.contrib.auth.tokens import default_token_generator
import logging
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
import random
from django.conf import settings
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model
from django.template import TemplateDoesNotExist
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)

User = get_user_model()


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class SendResetCodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

        try:
            code = random.randint(100000, 999999)
            cache.set(f'reset_code_{user.id}', code, timeout=300)  # Cache for 5 minutes (300 seconds)

            context = {
                'user': user,
                'code': code,
            }
            subject = 'Сброс пароля'
            try:
                html_message = render_to_string('password_reset_email.html', context)
            except TemplateDoesNotExist:
                return Response({'detail': 'Шаблон "password_reset_email.html" не найден'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            plain_message = strip_tags(html_message)
            from_email = settings.EMAIL_HOST_USER
            to = user.email

            email_message = EmailMultiAlternatives(subject, plain_message, from_email, [to])
            email_message.attach_alternative(html_message, "text/html")
            email_message.send()

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Код для сброса пароля отправлен на вашу электронную почту"},
                        status=status.HTTP_200_OK)


class VerifyResetCodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        code = request.data.get('code')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

        cached_code = cache.get(f'reset_code_{user.id}')
        if cached_code is None or str(cached_code) != str(code):
            return Response({"detail": "Неверный или просроченный код"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Код подтвержден"}, status=status.HTTP_200_OK)


class ResetPasswordWithCodeView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ResetPasswordWithCodeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Пароль был сброшен"}, status=status.HTTP_200_OK)


class CustomUserViewSet(UserViewSet):
    @action(["post"], detail=False)
    def reset_password(self, request, *args, **kwargs):
        serializer = djoser_settings.SERIALIZERS.password_reset(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user()

        if user:
            context = {"user": user}
            to = [get_user_email(user)]
            djoser_settings.EMAIL.password_reset(self.request, context).send(to)
            return Response(
                {"detail": f"Ссылка для сброса пароля отправлена на {user.email}"},
                status=status.HTTP_200_OK
            )

        return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Успешный выход из системы"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        CACHE_KEY = f'profile_id_{user.id}'
        cached_user = cache.get(CACHE_KEY)
        if cached_user:
            return Response(cached_user)
        serializer = UserProfileSerializer(user)
        cache.set(CACHE_KEY, serializer.data, CACHE_TIMEOUT)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        CACHE_KEY = f'profile_id_{user.id}'
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            cache.delete(CACHE_KEY)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateUser(UserViewSet):
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        kwargs['data'] = {"uid": self.kwargs['uid'], "token": self.kwargs['token']}
        return serializer_class(*args, **kwargs)

    def activation(self, request, *args, **kwargs):
        uid = kwargs.get('uid')
        token = kwargs.get('token')

        try:
            uid = decode_uid(uid)
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            signals.user_activated.send(sender=self.__class__, user=user, request=self.request)

            if djoser_settings.SEND_CONFIRMATION_EMAIL:
                context = {"user": user}
                to = [get_user_email(user)]
                djoser_settings.EMAIL.confirmation(self.request, context).send(to)

            return Response({"detail": _("Пользователь успешно активирован.")}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": _("Просроченный токен для данного пользователя.")}, status=status.HTTP_400_BAD_REQUEST)
