from rest_framework import serializers
from dj_rest_auth.serializers import UserDetailsSerializer as BaseUserDetailsSerializer
from django.contrib.auth.models import User
from allauth.account import app_settings as allauth_settings
from .models import CustomUser


class UserDetailsSerializer(BaseUserDetailsSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'image',
                  'birth_date', 'phone_number', 'country', 'user_id']
