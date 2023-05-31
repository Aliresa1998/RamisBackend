from django.db.models import Model
from rest_framework import serializers
from dj_rest_auth.serializers import LoginSerializer, UserDetailsSerializer as BaseUserDetailsSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from allauth.account import app_settings as allauth_settings
from .models import CustomUser, Message, User
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'image',
                  'birth_date', 'phone_number', 'country', 'user_id', "email"]

    def to_representation(self, obj):
        data = super().to_representation(obj)
        try:
            data['email'] = self.context['email']
        except KeyError:
            data['email'] = self.context['request'].data["email"]
            data['username'] = self.context['request'].data['username']
        return data


class UserDetailsSerializer(BaseUserDetailsSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']


class MessageSerializer(serializers.ModelSerializer):
    recipient = serializers.ListField()

    class Meta:
        model = Message
        fields = ['id', 'sender_id', 'recipient',
                  'subject', 'body', 'created_at', 'is_read', 'send_all']

    def save(self, **kwargs):
        sender_id = self.context['sender_id']
        if self.validated_data['send_all'] == True:
            messages = [
                Message(
                    sender_id=sender_id,
                    recipient_id=recipient_id,
                    subject=self.validated_data['subject'],
                    body=self.validated_data['body'],
                    is_read=self.validated_data['is_read'],
                    send_all=self.validated_data['send_all']
                ) for recipient_id in list(User.objects.values_list('id', flat=True))
            ]
            Message.objects.bulk_create(messages)
            return messages
        elif isinstance(self.validated_data['recipient'], list) and not self.validated_data['send_all']:
            messages = [
                Message(
                    sender_id=sender_id,
                    recipient_id=recipient_id,
                    subject=self.validated_data['subject'],
                    body=self.validated_data['body'],
                    is_read=self.validated_data['is_read'],
                    send_all=self.validated_data['send_all']
                ) for recipient_id in self.validated_data['recipient']
            ]
            Message.objects.bulk_create(messages)
            return messages
        # else:
        #     return super().save(sender_id=sender_id, **kwargs)


class InboxMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender_id', 'recipient',
                  'subject', 'body', 'created_at', 'is_read', 'send_all']


class EditUserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', ]
