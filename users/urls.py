from django.urls import path, re_path
from dj_rest_auth.registration.views import RegisterView, VerifyEmailView, ConfirmEmailView
from dj_rest_auth.views import LoginView, LogoutView
from rest_framework import routers


from .views import AdminChangePassowrdView, AdminCloseTicketView, AdminCreateTicketView, AdminTicketMessageView, AllProfileView, DocumentView, EditInformationView, ProfileViewSet, SendMessageAPIView, InboxAPIView, AdminEditUserNameView, TicketIsReadView, UserCloseTicketView, UserCreateTicketView,UserTicketMessageView

router = routers.DefaultRouter()
router.register('', ProfileViewSet, basename='profile')
urlpatterns = [
                  path('account-confirm-email/<str:key>/', ConfirmEmailView.as_view()),
                  path('register/', RegisterView.as_view(), name='account_signup'),
                  path('login/', LoginView.as_view(), name='account_login'),
                  path('logout/', LogoutView.as_view(), name='account_logout'),
                  path('all_profile/', AllProfileView.as_view()),
                  path('send-message/', SendMessageAPIView.as_view(), name='send_message'),
                  path('inbox/', InboxAPIView.as_view(), name='inbox'),
                  path('admin/change-username/', AdminEditUserNameView.as_view(), name='admin-edit-username'),
                  path('admin/change-password/', AdminChangePassowrdView.as_view(), name='admin-change-password'),
                  path('edit-information/', EditInformationView.as_view(), name='edit-informations'),
                  path('create-ticket/', UserCreateTicketView.as_view(), name='create-ticket'),
                  path('ticket/', UserTicketMessageView.as_view(), name='ticket'),
                  path('close-ticket/', UserCloseTicketView.as_view(), name='close-ticket'),
                  path('isread-ticket/', TicketIsReadView.as_view(), name='isread-ticket'),
                  path('document/', DocumentView.as_view(), name='document'),
                  path('admin/ticket/', AdminTicketMessageView.as_view(), name='admin-ticket'),
                  path('admin/create-ticket/', AdminCreateTicketView.as_view(), name='admin-create-ticket'),
                  path('admin/status-ticket/', AdminCloseTicketView.as_view(), name='admin-close/open-ticket'),
                  path('verify-email/',
                       VerifyEmailView.as_view(), name='account_email'),
                  path('account-confirm-email/',
                       VerifyEmailView.as_view(), name='account_email_verification_sent'),
                  re_path(r'^account-confirm-email/(?P<key>[-:\w]+)/$',
                          VerifyEmailView.as_view(), name='account_confirm_email'),

              ] + router.urls
