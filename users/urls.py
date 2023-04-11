from django.urls import path, re_path
from dj_rest_auth.registration.views import RegisterView, VerifyEmailView, ConfirmEmailView
from dj_rest_auth.views import LoginView, LogoutView
from rest_framework import routers
from .views import ProfileViewSet

router = routers.DefaultRouter()
router.register('', ProfileViewSet, basename='profile')
urlpatterns = [
                  path('account-confirm-email/<str:key>/', ConfirmEmailView.as_view()),
                  path('register/', RegisterView.as_view(), name='account_signup'),
                  path('login/', LoginView.as_view(), name='account_login'),
                  path('logout/', LogoutView.as_view(), name='account_logout'),
                  path('verify-email/',
                       VerifyEmailView.as_view(), name='account_email'),
                  path('account-confirm-email/',
                       VerifyEmailView.as_view(), name='account_email_verification_sent'),
                  re_path(r'^account-confirm-email/(?P<key>[-:\w]+)/$',
                          VerifyEmailView.as_view(), name='account_confirm_email'),

              ] + router.urls
