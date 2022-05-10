from django.conf import settings
from django.core import exceptions
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from dj_rest_auth.serializers import LoginSerializer as DefaultLoginSerializer
from pyhunter import PyHunter
import clearbit
from rest_framework import serializers
from re import compile as re_compile

from .models import User

NAME_REGEX = re_compile(r'^\w+$')
PYHUNTER = PyHunter(settings.HUNTERIO_API_KEY)
clearbit.key = settings.CLEARBIT_API_KEY


class LoginSerializer(DefaultLoginSerializer):
    def __init__(self, *args, **kwargs):
        kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        self.fields.pop('username')


class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

    def validate_email(self, value):
        try:
            hunterio_response = PYHUNTER.email_verifier(value)
        except Exception as e:
            raise serializers.ValidationError(_("Unable to verify email address. Please try again later."))
        if hunterio_response['status'] in ('invalid', 'unknown'):
            raise serializers.ValidationError(_(
                "Either e-mail address is invalid, or it's not possible to verify it. Please try with another one."
            ))
        return value

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        errors = {}
        try:
            # validate the password and catch the exception
            validate_password(password=attrs['password2'])
        # the exception raised here is different from serializers.ValidationError
        except exceptions.ValidationError as e:
            errors['password1'] = e.messages
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def save(self, request):
        clearbit_response = None
        try:
            clearbit_response = clearbit.Enrichment.find(email=self.validated_data['email'])
        except Exception as e:
            pass
        extra_fields = {}
        if clearbit_response and 'person' in clearbit_response and 'name' in clearbit_response['person']:
            extra_fields['first_name'] = clearbit_response['person']['name']['givenName']
            extra_fields['last_name'] = clearbit_response['person']['name']['familyName']
        user = User.objects.create_user(self.validated_data['email'], self.validated_data['password1'], **extra_fields)
        return user


class UserDetailsSerializer(serializers.ModelSerializer):
    first_name = serializers.RegexField(NAME_REGEX, min_length=2, max_length=30)
    last_name = serializers.RegexField(NAME_REGEX, min_length=2, max_length=30)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')
        read_only_fields = ('email',)

    def __init__(self, *args, **kwargs):
        kwargs.pop('fields', None)
        without_email = kwargs.pop('without_email', None)
        super().__init__(*args, **kwargs)
        if without_email:
            self.fields.pop('email')

