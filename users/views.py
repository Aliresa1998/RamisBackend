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
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView, RetrieveAPIView
from rest_framework.decorators import action
from rest_framework.views import APIView
from xhtml2pdf import pisa
from users.permissions import AdminAccessPermission
from .models import CustomUser, Document, Message, Ticket, Plan
from .serializers import AdminChangePasswordSerializer, AdminCloseTicketSerializer, AdminCreateTicketSerializer, \
    AdminEditUserNameSerializer, AdminGetTicketSerializer, AdminTicketMessageSerializer, DocumentSerializer, \
    EditInformationSerializer, GetTicketSerializer, InboxMessageSerializer, IsReadMessageSerializer, MessageSerializer, \
    PlanListSerializer, \
    ProfileSerializer, AdminUserPlanSerializer, AdminAllRequestSerializer, \
    TicketIsReadSerializer, TicketMessageSerializer, UserCloseTicketSerializer, UserCreateTicketSerializer, \
    UserDetailsSerializer, UpdateImageSerializer, PlanSerializer, GetPlansSerializer, GetDocumentSerializer, \
    DeletePlanSerializer, DetailPlanSerializer
from .pagination import CustomPagination
from django.urls import reverse
from azbankgateways import bankfactories, models as bank_models, default_settings as settings
from azbankgateways.exceptions import AZBankGatewaysException
from data.models import Wallet
from django.conf import settings
import requests
import json
import redis

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


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
        return redirect('http://panel.mycryptoprop.com/password-recovery/?uidb64=' + uid + '&token=' + token)


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
            return Response({"detail": "لطفا نام کاربری مورد نظر را به درستی وارد کنید."},
                            status=status.HTTP_400_BAD_REQUEST)
        if str(old_username) == str(new_username):
            return Response({"detail": "نام کاربری جدید با نام کابربری قبلی برابر است لطفا نام کابری جدید کنید."},
                            status=status.HTTP_400_BAD_REQUEST)
        User.objects.filter(username=old_username).update(
            username=new_username)
        return Response({"detail": "نام کاربری با موفقیت تغییر کرد."}, status=status.HTTP_200_OK)


class AdminChangePassowrdView(UpdateAPIView):
    permission_classes = [AdminAccessPermission]
    serializer_class = AdminChangePasswordSerializer

    def put(self, request, *args, **kwargs):
        try:
            user = User.objects.get(username=request.data['username'])
        except KeyError:
            return Response({"detail": "لطفا آیدی کاربر مورد نظر را به درستی وارد کنید."},
                            status=status.HTTP_400_BAD_REQUEST)
        user.set_password(request.data['new_password'])
        user.save()
        return Response({'detail': 'رمز عبور کاربر با موفقیت تغییر کرد'}, status=status.HTTP_200_OK)


class EditInformationView(UpdateAPIView):
    serializer_class = EditInformationSerializer
    http_method_names = ['patch']

    def patch(self, request, *args, **kwargs):
        user = User.objects.get(username=request.user)
        if not request.data:
            return Response({'detail': 'تمامی فیلد ها خالی میباشند'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            if request.data['new_username'] and request.data['old_password'] and request.data['new_password1'] and \
                    request.data['new_password2']:
                return Response({'detail':
                                     'برای تغییر نام کاربری تنها فیلد مربوط به نام کاربری را پر کنید و برای تغییر رمز عبور تنها فیلد های مربوط به رمز عبور را پر کنید.'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            try:
                if str(request.data['new_username']) == str(user.username):
                    return Response({'detail': 'نام کاربری قبلی با نام کاربری فعلی برابر میباشد.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                elif str(request.data['new_username']) != str(user.username):
                    User.objects.filter(username=user).update(
                        username=request.data['new_username'])
                    return Response({'detail': 'نام کاربری با موفقیت تغییر کرد.'}, status=status.HTTP_200_OK)
            except KeyError:
                if request.data['old_password'] and request.data['new_password1'] and request.data['new_password2']:
                    password = EditInformationSerializer(
                        data=request.data, context={'request': request})
                    password.is_valid(raise_exception=True)
                    user.set_password(password.data['new_password1'])
                    user.save()
                    return Response({'detail': 'رمز عبور شما با موفقیت تغییر کرد'}, status=status.HTTP_200_OK)


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
        return Response({'detail': 'تیکت بسته شد'}, status=status.HTTP_200_OK)


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
            return Response({'detail': f'تیکت {ticket_status} شد'}, status=status.HTTP_200_OK)
        except:
            return Response({'detail': 'آیدی تیکت درست نمیباشد.'}, status=status.HTTP_400_BAD_REQUEST)


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
        # Create this template file
        template = get_template('users/profiles_report.html')

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


class AdminAllPlanView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserPlanSerializer
    permission_classes = [AdminAccessPermission]


class AdminSinglePlanView(RetrieveAPIView):
    serializer_class = AdminUserPlanSerializer
    permission_classes = [AdminAccessPermission]

    def get_queryset(self):
        return User.objects.filter(id=self.kwargs['pk'])


class AdminAllTransactionView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = AdminAllRequestSerializer
    permission_classes = [AdminAccessPermission]


class AdminSingleTransactionView(RetrieveAPIView):
    serializer_class = AdminAllRequestSerializer
    permission_classes = [AdminAccessPermission]

    def get_queryset(self):
        return User.objects.filter(id=self.kwargs['pk'])


class Unread(APIView):
    def get(self, request, *args, **kwargs):

        if self.kwargs['type'] == "massage":
            massage = Message.objects.filter(is_read=False)
            return Response(massage.count(), status=status.HTTP_200_OK)
        elif self.kwargs['type'] == "ticket":
            ticket = Ticket.objects.filter(is_read=False)
            return Response(ticket.count(), status=status.HTTP_200_OK)
        else:
            return Response({"detail": "نوع پیام انتخابی درست نمیباشد"}, status=status.HTTP_400_BAD_REQUEST)


class PlanView(APIView):
    serializer_class = PlanSerializer

    def post(self, request, *args, **kwargs):
        plan = Plan.objects.filter(id=self.request.data['plan_id'], is_delete=False).first()
        if plan is None:
            return Response({"error": "پلن مورد نظر یافت نشد ."})
        data = {
            'amount': plan.amount,
            'plan_id': plan.id
        }
        json_data = json.dumps(data)
        redis_client.set(f"{self.request.user}", json_data)
        amount = plan.amount
        req_data = {
            "merchant_id": MERCHANT,
            "amount": amount,
            "callback_url": CallbackURL,
            "description": description,
        }
        req_header = {"accept": "application/json",
                      "content-type": "application/json'"}
        req = requests.post(url=ZP_API_REQUEST, data=json.dumps(
            req_data), headers=req_header)
        authority = req.json()['data']['authority']
        if len(req.json()['errors']) == 0:
            return Response(ZP_API_STARTPAY.format(authority=authority))

        else:
            e_code = req.json()['errors']['code']
            e_message = req.json()['errors']['message']
            return Response(f"Error code: {e_code}, Error Message: {e_message}")


class GetPlan(ListAPIView):
    serializer_class = GetPlansSerializer

    def get_queryset(self):
        customuser = CustomUser.objects.get(user=self.request.user)
        return Plan.objects.filter(customuser=customuser)


class GetDocumentById(ListAPIView):
    serializer_class = GetDocumentSerializer

    def get_queryset(self):
        return Document.objects.filter(user=self.kwargs["user"])


MERCHANT = "7243cd2f-d798-40ef-bf12-82eb05c79454"
ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"
description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"
CallbackURL = 'https://panel.mycryptoprop.com/done-payment/'


class PlanVerifyView(APIView):
    def get(self, request):
        data = redis_client.get(f"{self.request.user}")
        data = json.loads(data)
        t_status = request.GET.get('Status')
        t_authority = request.GET['Authority']
        if request.GET.get('Status') == 'OK':
            req_header = {"accept": "application/json",
                          "content-type": "application/json'"}
            req_data = {
                "merchant_id": MERCHANT,
                "amount": data['amount'],
                "authority": t_authority
            }
            req = requests.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
            if len(req.json()['errors']) == 0:
                t_status = req.json()['data']['code']
                if t_status == 100:
                    plan = Plan.objects.filter(id=data['plan_id']).first()
                    custom_user, created = CustomUser.objects.get_or_create(user=self.request.user)
                    custom_user.plan = plan
                    walet = Wallet.objects.get(user=self.request.user)
                    new_balance = walet.balance + data['amount']
                    Wallet.objects.filter(user=self.request.user).update(balance=new_balance)

                    return Response({'text': str(req.json()['data']['ref_id'])}, status=status.HTTP_201_CREATED)
                elif t_status == 101:

                    return Response({"text": str(req.json()['data']['message'])}, status=status.HTTP_200_OK)
                else:

                    return Response({"error": str(req.json()['data']['message'])}, status=status.HTTP_424_FAILED_DEPENDENCY)

            else:
                e_code = req.json()['errors']['code']
                e_message = req.json()['errors']['message']
                return Response({"error": f"Error code: {e_code}, Error Message: {e_message}"})
        else:
            return Response({"error": 'Transaction failed or canceled by user'})


class DetailPlanView(UpdateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'delete':
            return DeletePlanSerializer
        return DetailPlanSerializer

    def put(self, request, *args, **kwargs):
        try:
            amount = self.request.data.get('amount')
            plan = self.request.data.get('plan')

            if plan is None:
                plan_instance = Plan.objects.filter(id=self.kwargs['id']).first()
                plan_instance.amount = amount
                plan_instance.save()
            else:
                plan_instance = Plan.objects.filter(id=self.kwargs['id']).first()
                plan_instance.plan = plan
                plan_instance.amount = amount
                plan_instance.save()

            data = DetailPlanSerializer(plan_instance)
            return Response(data.data, status=status.HTTP_200_OK)

        except Plan.DoesNotExist:
            return Response("Plan not found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        Plan.objects.filter(id=self.kwargs['id']).update(is_delete=True)
        return Response(status=status.HTTP_200_OK)


class CreatePlanView(CreateAPIView):
    permission_classes = [IsAuthenticated, AdminAccessPermission]
    serializer_class = DetailPlanSerializer
    queryset = Plan.objects.all()


class UserHavePlanView(APIView):
    def get(self, request, *args, **kwargs):

        if CustomUser.objects.get(user=self.request.user).plan:
            return Response({"detail": True})
        else:
            return Response({"detail": False})


class AllPlanListView(ListAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanListSerializer
    permission_classes = [IsAuthenticated]
