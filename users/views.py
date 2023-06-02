from django.shortcuts import redirect
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView
from rest_framework.decorators import action
from dj_rest_auth.views import PasswordResetConfirmView, PasswordChangeView
from rest_framework.views import APIView
from users.permissions import AdminAccessPermission
from .models import CustomUser, Message
from .serializers import AdminChangePasswordSerializer, AdminEditUserNameSerializer, InboxMessageSerializer, MessageSerializer, ProfileSerializer, UserDetailsSerializer, \
    EditUserNameSerializer, CustomPasswordChangeSerializer


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


class EditUserNameView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EditUserNameSerializer

    def post(self, request, *args, **kwargs):
        old_username = request.user
        try:
            new_username = self.request.data['username']
        except KeyError:
            return Response("لطفایوزر نیم خود را به درستی وارد کنید.", status=status.HTTP_400_BAD_REQUEST)
        if str(old_username) == str(new_username):
            return Response("یوز نیم جدید شما با یوزر نیم قبلی شما برار است لطفا یوزر نیم جدید خود را وارد کنید.",
                            status=status.HTTP_400_BAD_REQUEST)
        User.objects.filter(username=old_username).update(
            username=new_username)
        return Response("یوزر نیم شما با موفقیت تغییر کرد.", status=status.HTTP_200_OK)


class CustomPasswordChangeView(PasswordChangeView):
    serializer_class = CustomPasswordChangeSerializer


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

