from django.shortcuts import redirect
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.decorators import action
from dj_rest_auth.views import PasswordResetConfirmView

from users.permissions import AdminAccessPermission
from .models import CustomUser
from .serializers import ProfileSerializer, UserDetailsSerializer


class ProfileViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    """
        API for update and get profile
    """

    queryset = CustomUser.objects.all()
    # def get_queryset(self):
    #     return CustomUser.objects.filter(user_id=self.request.user.id)
    serializer_class = ProfileSerializer

    @action(detail=False, methods=['GET', 'PUT'])
    def profile(self, request):
        (customuser, created) = CustomUser.objects.get_or_create(
            user_id=request.user.id)
        if request.method == 'GET':
            serializer = ProfileSerializer(customuser)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = ProfileSerializer(customuser, data=request.data)
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
    # def get_serializer_context(self):
    #     return {'user_id':self.request.user.id}
    
