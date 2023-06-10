from contextlib import nullcontext
from django.db.models import Model
from rest_framework import serializers
from dj_rest_auth.serializers import LoginSerializer, UserDetailsSerializer as BaseUserDetailsSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from .models import CustomUser, Message, Ticket, User, Document
from dj_rest_auth.serializers import PasswordChangeSerializer

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name',
                  'birth_date', 'phone_number', 'address', 'user_id', 'national_code', "email"]

    def to_representation(self, obj):
        data = super().to_representation(obj)
        user_email = User.objects.get(id=data['user_id']).email
        try:
            data['email'] = user_email
        except KeyError:
            data['email'] = user_email
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


class InboxMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender_id', 'recipient',
                  'subject', 'body', 'created_at', 'is_read', 'send_all']


class AdminEditUserNameSerializer(serializers.ModelSerializer):
    new_username = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'new_username']


class AdminChangePasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'new_password']


class EditInformationSerializer(PasswordChangeSerializer):
    old_password = serializers.CharField(required=True)
    new_username = serializers.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'] = serializers.CharField()
        self.fields['new_username'] = serializers.CharField(required=False)

    def validate_old_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('رمز قدیمی شما درست نمیباشد .')
        elif self.request.data['new_password1'] != self.request.data['new_password2']:
            raise serializers.ValidationError('رمز ۱ با رمز ۲ برابر نیست .')
        elif self.request.data['old_password'] == self.request.data["new_password1"]:
            raise serializers.ValidationError(
                "رمز جدید شما با رمز قبلی یکی است .")
        return value

    class Meta:
        model = User
        fields = ['new_username', 'old_password',
                  'new_password1', 'new_password2']


class UserCreateTicketSerializer(serializers.ModelSerializer):
    body = serializers.ListField(read_only=True)
    message = serializers.CharField(required=True)
    image = serializers.ImageField(required=False)

    class Meta:
        model = Ticket
        fields = ['body', 'message', 'image']

    def save(self, **kwargs):
        try:
            message = {f'{self.context["user"]}': self.validated_data['message'],
                       'image': self.validated_data['image']}
        except KeyError:
            message = {
                f'{self.context["user"]}': self.validated_data['message']}
        body = list()
        body.append(message)
        ticket = Ticket.objects.create(
            sender=self.context['user'], body=body, receiver='admin')
        return ticket


class GetTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'body', 'status', 'receiver','is_read']


class TicketMessageSerializer(serializers.ModelSerializer):
    body = serializers.ListField(read_only=True)
    message = serializers.CharField(required=True)
    image = serializers.ImageField(required=False)
    id = serializers.IntegerField(required=True)

    class Meta:
        model = Ticket
        fields = ['id', 'body', 'message', 'image']

    def save(self, **kwargs):
        try:
            message = {f'{self.context["user"]}': self.validated_data['message'],
                       'image': self.validated_data['image']}
        except KeyError:
            message = {
                f'{self.context["user"]}': self.validated_data['message'], }
        try:
            ticket = Ticket.objects.get(id=self.validated_data['id'])
            if ticket.status != 'close':
                body = ticket.body
                body.append(message)
                ticket = Ticket.objects.filter(
                    id=self.validated_data['id']).update(body=body, is_read=False)
                return ticket
            return 'تیکت بسته میباشد'
        except ValueError:
            raise serializers.ValidationError(
                'آیدی برای تیکت مورد نظر درست نمیباشد')


class AdminCreateTicketSerializer(serializers.ModelSerializer):
    body = serializers.ListField(read_only=True)
    message = serializers.CharField(required=True)
    image = serializers.ImageField(required=False)
    receiver = serializers.CharField(required=True)

    class Meta:
        model = Ticket
        fields = ['body', 'message', 'image', 'receiver']

    def save(self, **kwargs):
        try:
            message = {f'admin {self.context["user"]}': self.validated_data['message'],
                       'image': self.validated_data['image']}
        except KeyError:
            message = {
                f'admin {self.context["user"]}': self.validated_data['message']}
        body = list()
        body.append(message)
        ticket = Ticket.objects.create(
            sender=self.context['user'], body=body, receiver=self.validated_data['receiver'])
        return ticket


class AdminTicketMessageSerializer(serializers.ModelSerializer):
    message = serializers.CharField(required=True)
    image = serializers.ImageField(required=False)
    id = serializers.IntegerField(required=True)

    class Meta:
        model = Ticket
        fields = ['id', 'message', 'image']

    def save(self, **kwargs):
        try:
            message = {f'admin {self.context["user"]}': self.validated_data['message'],
                       'image': self.validated_data['image']}
        except KeyError:
            message = {
                f'admin {self.context["user"]}': self.validated_data['message']}
        try:
            ticket = Ticket.objects.get(id=self.validated_data['id'])
            if ticket.status != 'close':
                body = ticket.body
                body.append(message)
                ticket = Ticket.objects.filter(
                    id=self.validated_data['id']).update(body=body,is_read=False)
                return ticket
            return 'تیکت بسته میباشد برای استفاده دوباره میتوانید آن را باز کنید'
        except ValueError:
            raise serializers.ValidationError('ایدی تیکت درست نمیباشد')


class AdminGetTicketSerializer(serializers.ModelSerializer):
    sender = serializers.CharField()

    class Meta:
        model = Ticket
        fields = '__all__'


class UserCloseTicketSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = Ticket
        fields = ['id']


class AdminCloseTicketSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    status = serializers.CharField(required=True)

    class Meta:
        model = Ticket
        fields = ['id', 'status']


class TicketIsReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = Ticket
        fields = ['id']
    def save(self, **kwargs):
        try:
            ticket = Ticket.objects.filter(id=self.validated_data['id']).update(is_read=True)
            return ticket
        except ValueError:
            raise serializers.ValidationError('ایدی تیکت درست نمیباشد')

class DocumentSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Document
        fields = ['user_id', 'profile_image', 'identity_card',
                  'birth_certificate', 'Commitment_letter']
