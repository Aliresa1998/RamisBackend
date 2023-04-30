from django.urls import path
from .views import OhlcData, CryptoList, CreateTrade, Historytrade, UpdateHistoryTrade, CreateWallet, WithdrawWallet, \
    GetWallet

urlpatterns = [
    path('data/', OhlcData.as_view(), name='data'),
    path('crypto_list/', CryptoList.as_view(), name='crypto_list'),
    path('trade/', CreateTrade.as_view(), name='create_trade'),
    path("history/", Historytrade.as_view(), name='history'),
    path("history/<int:pk>", UpdateHistoryTrade.as_view(), name='history'),
    path("wallet/", CreateWallet.as_view(), name='wallet'),
    path("withdraw/", WithdrawWallet.as_view(), name='withdraw_wallet'),
    path('get-wallet/', GetWallet.as_view(), name='get_wallet'),
]
