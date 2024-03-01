import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import serializers
from dj_rest_auth.serializers import UserDetailsSerializer as BaseUserDetailsSerializer
from .models import CustomUser, Message, Ticket, User, Document, Plan, CryptoPayment
from dj_rest_auth.serializers import PasswordChangeSerializer
from data.models import WalletHistory
from data.serializers import ChallangeSerializer, GetWalletSerializer, HistorySerializer, WalletHistorySerializer

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


class DocumentSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Document
        fields = ['user_id', 'profile_image', 'identity_card',
                  'birth_certificate', 'Commitment_letter']


class UserDetailsSerializer(BaseUserDetailsSerializer):
    profile = ProfileSerializer()
    document = DocumentSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile', 'document']


class MessageSerializer(serializers.ModelSerializer):
    recipient = serializers.ListField()

    class Meta:
        model = Message
        fields = ['id', 'sender_id', 'recipient',
                  'subject', 'body', 'created_at', 'send_all']

    def save(self, **kwargs):
        sender_id = self.context['sender_id']
        if self.validated_data['send_all']:
            messages = [
                Message(
                    sender_id=sender_id,
                    recipient_id=recipient_id,
                    subject=self.validated_data['subject'],
                    body=self.validated_data['body'],
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
                    send_all=self.validated_data['send_all']
                ) for recipient_id in self.validated_data['recipient']
            ]
            Message.objects.bulk_create(messages)
            return messages


class InboxMessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField()
    recipient = serializers.CharField()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient',
                  'subject', 'body', 'created_at', 'is_read', 'send_all']


class IsReadMessageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = Message
        fields = ['id']


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
    subject = serializers.CharField(required=True)

    class Meta:
        model = Ticket
        fields = ['body', 'subject', 'message', 'image']

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
            sender=self.context['user'], subject=self.validated_data['subject'], body=body, receiver='admin')
        return ticket


class GetTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'subject', 'body', 'status', 'receiver',
                  'is_read', 'created_at', 'last_modified']


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
                    id=self.validated_data['id']).update(body=body, is_read=False,
                                                         last_modified=datetime.datetime.now())
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
    subject = serializers.CharField(required=True)

    class Meta:
        model = Ticket
        fields = ['subject', 'body', 'message', 'image', 'receiver']

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
            sender=self.context['user'], subject=self.validated_data['subject'], body=body,
            receiver=self.validated_data['receiver'])
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
                    id=self.validated_data['id']).update(body=body, is_read=False,
                                                         last_modified=datetime.datetime.now())
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
            ticket = Ticket.objects.filter(
                id=self.validated_data['id']).update(is_read=True)
            return ticket
        except ValueError:
            raise serializers.ValidationError('ایدی تیکت درست نمیباشد')


class UpdateImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['profile_image']


class SimpleProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name')


class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['profile_image']


class AdminUserPlanSerializer(serializers.ModelSerializer):
    profile = SimpleProfileSerializer()
    document = ProfileImageSerializer()
    challange = ChallangeSerializer()
    trades = HistorySerializer(many=True)
    wallet = GetWalletSerializer()

    class Meta:
        model = User
        fields = ('id', 'profile', 'document',
                  'wallet', 'challange', 'trades')


class SimpleWallerHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletHistory
        fields = ('created', 'amount', 'transaction', 'wallet_destination')


class AdminAllRequestSerializer(serializers.ModelSerializer):
    profile = SimpleProfileSerializer()
    document = ProfileImageSerializer()
    wallet_history = SimpleWallerHistorySerializer(many=True)

    class Meta:
        model = User
        fields = ('id', 'profile', 'document', 'wallet_history')
        # fields = ['profile_image', 'identity_card', 'birth_certificate', 'Commitment_letter']


class PlanSerializer(serializers.ModelSerializer):
    plan_id = serializers.IntegerField(required=True)

    class Meta:
        model = Plan
        fields = ['plan_id']


class GetPlansSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["plan"]


class GetDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['user_id', 'profile_image', 'identity_card',
                  'birth_certificate', 'Commitment_letter']


class DeletePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['is_delete']


class DetailPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'


class PlanListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['plan', 'amount', 'id']


class CryptoPaymentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = CryptoPayment
        fields = ['plan', 'image', "user"]


class UserDetail(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class PlanDetail(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['plan']


class GetCryptoPaymentSerializer(serializers.ModelSerializer):
    user = UserDetail()
    plan = PlanDetail()

    class Meta:
        model = CryptoPayment
        fields = ['id', 'user', 'plan', 'image', 'status']


class UpdateCryptoPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoPayment
        fields = ['status']
