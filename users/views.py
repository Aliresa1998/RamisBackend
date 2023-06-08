from django.dispatch import receiver
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.db.models import Q
from dj_rest_auth.views import PasswordResetConfirmView, PasswordChangeView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView
from rest_framework.decorators import action
from rest_framework.views import APIView
from users.permissions import AdminAccessPermission
from .models import CustomUser, Message, Ticket
from .serializers import AdminChangePasswordSerializer, AdminCloseTicketSerializer, AdminCreateTicketSerializer, AdminEditUserNameSerializer, AdminGetTicketSerializer, AdminTicketMessageSerializer, EditInformationSerializer, GetTicketSerializer, InboxMessageSerializer, MessageSerializer, ProfileSerializer, TicketMessageSerializer, UserCloseTicketSerializer,  UserCreateTicketSerializer, UserDetailsSerializer


class ProfileViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    """
        API for update and get profile
    """

    queryset = CustomUser.objects.all()
    serializer_class = ProfileSerializer

    def get_serializer_context(self):
        return {'email': self.request.user.email}

    @action(detail=False, methods=['GET', 'PUT'])
    def profile(self, request):
        (customuser, created) = CustomUser.objects.get_or_create(
            user_id=request.user.id)
        if request.method == 'GET':
            serializer = ProfileSerializer(
                customuser, context={'email': self.request.user.email})
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = ProfileSerializer(customuser, data=request.data, context={
                'email': self.request.user.email})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    def get(self, request, uidb64=None, token=None, *args, **kwargs):
        try:
            uid = uidb64
            token = token
        except ValueError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return redirect('http://51.89.247.248:8080/password-recovery/?uidb64=' + uid + '&token=' + token)


class AllProfileView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailsSerializer
    permission_classes = [AdminAccessPermission]


class SendMessageAPIView(CreateAPIView):
    permission_classes = [AdminAccessPermission]
    serializer_class = MessageSerializer

    def get_serializer_context(self):
        return {'sender_id': self.request.user.id}


class InboxAPIView(ListAPIView):
    serializer_class = InboxMessageSerializer

    def get_queryset(self):
        message = Message.objects.filter(recipient=self.request.user)
        message.is_read = True
        return message


class AdminEditUserNameView(APIView):
    permission_classes = [AdminAccessPermission]
    serializer_class = AdminEditUserNameSerializer

    def post(self, request, *args, **kwargs):
        try:
            old_username = request.data['username']
            new_username = self.request.data['new_username']
        except KeyError:
            return Response("لطفا نام کاربری مورد نظر را به درستی وارد کنید.", status=status.HTTP_400_BAD_REQUEST)
        if str(old_username) == str(new_username):
            return Response("نام کاربری جدید با نام کابربری قبلی برابر است لطفا نام کابری جدید کنید.",
                            status=status.HTTP_400_BAD_REQUEST)
        User.objects.filter(username=old_username).update(
            username=new_username)
        return Response("نام کاربری با موفقیت تغییر کرد.", status=status.HTTP_200_OK)


class AdminChangePassowrdView(UpdateAPIView):
    permission_classes = [AdminAccessPermission]
    serializer_class = AdminChangePasswordSerializer

    def put(self, request, *args, **kwargs):
        try:
            user = User.objects.get(username=request.data['username'])
        except KeyError:
            return Response("لطفا آیدی کاربر مورد نظر را به درستی وارد کنید.", status=status.HTTP_400_BAD_REQUEST)
        user.set_password(request.data['new_password'])
        user.save()
        return Response('رمز عبور کاربر با موفقیت تغییر کرد', status=status.HTTP_200_OK)


class EditInformationView(UpdateAPIView):
    serializer_class = EditInformationSerializer
    http_method_names = ['patch']

    def patch(self, request, *args, **kwargs):
        user = User.objects.get(username=request.user)
        if not request.data:
            return Response('تمامی فیلد ها خالی میباشند', status=status.HTTP_400_BAD_REQUEST)
        try:
            if request.data['new_username'] and request.data['old_password'] and request.data['new_password1'] and request.data['new_password2']:
                return Response('برای تغییر نام کاربری تنها فیلد مربوط به نام کاربری را پر کنید و برای تغییر رمز عبور تنها فیلد های مربوط به رمز عبور را پر کنید.', status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            try:
                if str(request.data['new_username']) == str(user.username):
                    return Response('نام کاربری قبلی با نام کاربری فعلی برابر میباشد.', status=status.HTTP_400_BAD_REQUEST)
                elif str(request.data['new_username']) != str(user.username):
                    User.objects.filter(username=user).update(
                        username=request.data['new_username'])
                    return Response('نام کاربری با موفقیت تغییر کرد.', status=status.HTTP_200_OK)
            except KeyError:
                if request.data['old_password'] and request.data['new_password1'] and request.data['new_password2']:
                    password = EditInformationSerializer(
                        data=request.data, context={'request': request})
                    password.is_valid(raise_exception=True)
                    user.set_password(password.data['new_password1'])
                    user.save()
                    return Response('رمز عبور شما با موفقیت تغییر کرد', status=status.HTTP_200_OK)


class UserCreateTicketView(CreateAPIView):
    serializer_class = UserCreateTicketSerializer

    def get_serializer_context(self):
        return {'user': self.request.user}


class UserTicketMessageView(CreateAPIView, ListAPIView):
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetTicketSerializer
        return TicketMessageSerializer

    def get_serializer_context(self):
        return {'user': self.request.user}

    def get_queryset(self):
        return Ticket.objects.filter(Q(sender=self.request.user) | Q(receiver=self.request.user.username)).all()


class AdminCreateTicketView(CreateAPIView):
    permission_classes = [AdminAccessPermission]
    serializer_class = AdminCreateTicketSerializer

    def get_serializer_context(self):
        return {'user': self.request.user}


class AdminTicketMessageView(CreateAPIView, ListAPIView):
    permission_classes = [AdminAccessPermission]
    permission_classes = [AdminAccessPermission]
    queryset = Ticket.objects.exclude(body=[]).exclude(body=None).all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AdminGetTicketSerializer
        return AdminTicketMessageSerializer

    def get_serializer_context(self):
        return {'user': self.request.user}


class UserCloseTicketView(UpdateAPIView):
    serializer_class = UserCloseTicketSerializer

    def get_queryset(self):
        return Ticket.objects.filter(Q(sender=self.request.user) | Q(receiver=self.request.user.username)).all()

    def put(self, request, *args, **kwargs):
        serializer = UserCloseTicketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        Ticket.objects.filter(
            id=serializer.data['id']).update(status='Close')
        return Response('تیکت بسته شد', status=status.HTTP_200_OK)


class AdminCloseTicketView(UpdateAPIView):
    serializer_class = AdminCloseTicketSerializer
    permission_classes = [AdminAccessPermission]
    queryset = Ticket.objects.exclude(body=[]).exclude(body=None).all()

    def put(self, request, *args, **kwargs):
        serializer = AdminCloseTicketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket_status = str()
        ticket_status = 'بسته' if serializer.data['status'] == 'close' else 'باز'
        try:
            Ticket.objects.filter(
                id=serializer.data['id']).update(status=serializer.data['status'])
            return Response(f'تیکت {ticket_status} شد', status=status.HTTP_200_OK)
        except:
            return Response(f'آیدی تیکت درست نمیباشد.', status=status.HTTP_400_BAD_REQUEST)
