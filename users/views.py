from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.db.models import Q
from django.views import View
from django.http import HttpResponse
from django.template.loader import get_template
from dj_rest_auth.views import PasswordResetConfirmView
from rest_framework import status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView
from rest_framework.decorators import action
from rest_framework.views import APIView
from xhtml2pdf import pisa
from users.permissions import AdminAccessPermission
from .models import CustomUser, Document, Message, Ticket
from .serializers import AdminChangePasswordSerializer, AdminCloseTicketSerializer, AdminCreateTicketSerializer, \
    AdminEditUserNameSerializer, AdminGetTicketSerializer, AdminTicketMessageSerializer, DocumentSerializer, \
    EditInformationSerializer, GetTicketSerializer, InboxMessageSerializer, IsReadMessageSerializer, MessageSerializer, \
    ProfileSerializer, \
    TicketIsReadSerializer, TicketMessageSerializer, UserCloseTicketSerializer, UserCreateTicketSerializer, \
    UserDetailsSerializer, UpdateImageSerializer
from .pagination import CustomPagination


class ProfileViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    """
        API for update and get profile
    """

    serializer_class = ProfileSerializer

    def get_queryset(self):
        return CustomUser.objects.filter(user=self.request.user)

    @action(detail=False, methods=['GET', 'PUT'])
    def profile(self, request):
        (customuser, created) = CustomUser.objects.get_or_create(
            user_id=request.user.id, email=self.request.user.email)
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
        return redirect('http://51.89.247.248:8085/password-recovery/?uidb64=' + uid + '&token=' + token)


class AllProfileView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailsSerializer
    permission_classes = [AdminAccessPermission]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', "email"]
    pagination_class = CustomPagination


class SendMessageAPIView(CreateAPIView):
    permission_classes = [AdminAccessPermission]
    serializer_class = MessageSerializer

    def get_serializer_context(self):
        return {'sender_id': self.request.user.id}


class InboxAPIView(ListAPIView):
    serializer_class = InboxMessageSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['subject']
    pagination_class = CustomPagination

    def get_queryset(self):
        if self.kwargs['type'] == 'all':
            return Message.objects.filter(recipient=self.request.user).all()
        elif self.kwargs['type'] == 'read':
            return Message.objects.filter(
                recipient=self.request.user).filter(is_read=True).all()
        elif self.kwargs['type'] == 'unread':
            return Message.objects.filter(recipient=self.request.user).filter(
                is_read=False).all()


class MessageIsReadView(UpdateAPIView):
    queryset = Message.objects.all()
    serializer_class = IsReadMessageSerializer
    http_method_names = ['put']

    def put(self, request, *args, **kwargs):
        message = Message.objects.get(id=request.data['id'])
        message.is_read = True
        serializer = IsReadMessageSerializer(message, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


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
            if request.data['new_username'] and request.data['old_password'] and request.data['new_password1'] and \
                    request.data['new_password2']:
                return Response(
                    'برای تغییر نام کاربری تنها فیلد مربوط به نام کاربری را پر کنید و برای تغییر رمز عبور تنها فیلد های مربوط به رمز عبور را پر کنید.',
                    status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            try:
                if str(request.data['new_username']) == str(user.username):
                    return Response('نام کاربری قبلی با نام کاربری فعلی برابر میباشد.',
                                    status=status.HTTP_400_BAD_REQUEST)
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
    filter_backends = [filters.SearchFilter]
    search_fields = ['id', 'body', 'status', 'receiver', 'is_read']
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetTicketSerializer
        return TicketMessageSerializer

    def get_serializer_context(self):
        return {'user': self.request.user}

    def get_queryset(self):
        if self.kwargs['type'] == 'all':
            return Ticket.objects.filter(Q(sender=self.request.user) | Q(receiver=self.request.user.username)).all()
        elif self.kwargs['type'] == 'read':
            return Ticket.objects.filter(Q(sender=self.request.user) | Q(receiver=self.request.user.username)). \
                filter(is_read=True).all()
        elif self.kwargs['type'] == 'unread':
            return Ticket.objects.filter(Q(sender=self.request.user) | Q(receiver=self.request.user.username)). \
                filter(is_read=False).all()


class AdminCreateTicketView(CreateAPIView):
    permission_classes = [AdminAccessPermission]
    serializer_class = AdminCreateTicketSerializer

    def get_serializer_context(self):
        return {'user': self.request.user}


class AdminTicketMessageView(CreateAPIView, ListAPIView):
    permission_classes = [AdminAccessPermission]
    queryset = Ticket.objects.exclude(body=[]).exclude(body=None).all()
    pagination_class = CustomPagination

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


class TicketIsReadView(UpdateAPIView):
    serializer_class = TicketIsReadSerializer

    def put(self, request, *args, **kwargs):
        ticket = Ticket.objects.get(id=self.request.data['id'])
        serializer = TicketIsReadSerializer(ticket, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class DocumentView(CreateAPIView, ListAPIView):
    serializer_class = DocumentSerializer

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        (doc, created) = Document.objects.get_or_create(user_id=request.user.id)
        serializer = DocumentSerializer(doc, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetTicketBYID(ListAPIView):
    serializer_class = GetTicketSerializer

    def get_queryset(self, **kwargs):
        return Ticket.objects.filter(id=self.kwargs['id']).all()


class ProfilePictureUpdate(UpdateAPIView):
    serializer_class = UpdateImageSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        Document.objects.filter(user=self.request.user).update(
            profile_image=self.request.data['profile_image'])
        user_document = Document.objects.get(user=self.request.user)
        serializer = UpdateImageSerializer(user_document, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class GetInboxByID(ListAPIView):
    serializer_class = InboxMessageSerializer

    def get_queryset(self, **kwargs):
        return Message.objects.filter(id=self.kwargs['id'])


class ExportProfilesPDFView(View):
    def get(self, request):
        # Get all profiles
        profiles = CustomUser.objects.all()

        # Load the HTML template
        template = get_template('users/profiles_report.html')  # Create this template file

        # Prepare the context data
        context = {
            'profiles': profiles,
        }

        # Render the HTML template with the context data
        html = template.render(context)

        # Create a response object with PDF content
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="profiles.pdf"'

        # Generate the PDF from the HTML content
        pisa_status = pisa.CreatePDF(html, dest=response)

        if pisa_status.err:
            return HttpResponse('Error generating PDF')

        return response


class IsAdminView(ListAPIView):
    def get(self, request, *args, **kwargs):
        (user, created) = CustomUser.objects.get_or_create(user_id=request.user.id)
        is_admin = user.is_admin
        return Response(is_admin, status=status.HTTP_200_OK)


class Unread(APIView):
    def get(self, request, *args, **kwargs):

        if self.kwargs['type'] == "massage":
            massage = Message.objects.filter(is_read=False)
            return Response(massage.count(), status=status.HTTP_200_OK)
        elif self.kwargs['type'] == "ticket":
            ticket = Ticket.objects.filter(is_read=False)
            return Response(ticket.count(), status=status.HTTP_200_OK)
        else:
            return Response("نوع پیام انتخابی درست نمیباشد", status=status.HTTP_400_BAD_REQUEST)
