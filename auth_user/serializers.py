from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.settings import api_settings
from .models import CustomUser
from rest_framework import serializers, exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from utils.translate import translate_text

User = get_user_model()


class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    re_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = '__all__'
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'required': True},
            're_password': {'required': True},
        }

    def validate(self, data):
        if data['password'] != data['re_password']:
            raise serializers.ValidationError("Пароли не совпадают")
        if data['age'] < 0 or data['age'] > 110:
            raise serializers.ValidationError("Неверный возраст")
        return data

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            gender=validated_data.get('gender', ''),
            age=validated_data.get('age', '')
        )
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'


class CustomUserSerializer(UserProfileSerializer):
    pass


class UserCommentSerializer(UserProfileSerializer):
    class Meta(UserProfileSerializer.Meta):
        fields = ['first_name', 'last_name']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        'no_active_account': _('Активная учетная запись с указанными учетными данными не найдена'),
        'wrong_password': _('Неверный пароль. Пожалуйста, попробуйте снова.'),
    }

    def _authenticate_user_email(self, email, password, request):
        self.user = authenticate(email=email, password=password, request=request)
        return self.user

    def validate(self, attrs):
        email = attrs.get(self.username_field)
        password = attrs.get('password')
        request = self.context.get('request')

        user = self._authenticate_user_email(email, password, request)

        if user is None:
            try:
                user = get_user_model().objects.get(**{self.username_field: email})
                if not user.check_password(password):
                    raise exceptions.AuthenticationFailed(
                        _('Неверный пароль. Пожалуйста, попробуйте снова')
                    )
            except get_user_model().DoesNotExist:
                raise exceptions.AuthenticationFailed(
                    _('Активная учетная запись с указанными учетными данными не найдена')
                )

        data = super().validate(attrs)
        refresh = self.get_token(user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, user)

        return data


class ResetPasswordWithCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)
    re_new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')
        new_password = attrs.get('new_password')
        re_new_password = attrs.get('re_new_password')

        if new_password != re_new_password:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "Пользователь не найден."})

        cached_code = cache.get(f'reset_code_{user.id}')
        if cached_code is None or str(cached_code) != str(code):
            raise serializers.ValidationError({"code": "Неверный или просроченный код."})

        # Invalidate the reset code immediately after verification
        cache.delete(f'reset_code_{user.id}')

        # Validate the new password strength
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            translated_messages = [translate_text(message) for message in e.messages]
            raise serializers.ValidationError({"new_password": translated_messages})

        attrs['user'] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        cache.delete(f'reset_code_{user.id}')
        return user
