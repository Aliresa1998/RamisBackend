from django.urls import path
from .views import AccountGrowthView, GetChallangeView, UpgradeChallangeView, OhlcData, CryptoList, CreateTrade, \
    Historytrade, UpdateHistoryTrade, CreateWallet, WalletHistoryView, WithdrawWallet, \
    GetWallet

urlpatterns = [
    path('data/', OhlcData.as_view(), name='data'),
    path('crypto_list/', CryptoList.as_view(), name='crypto_list'),
    path('trade/', CreateTrade.as_view(), name='create_trade'),
    path("history/<str:type>", Historytrade.as_view(), name='history'),
    path("close/<int:pk>/", UpdateHistoryTrade.as_view(), name='history_without_leverage'),
    path("deposit-wallet/", CreateWallet.as_view(), name='wallet'),
    path("withdraw/", WithdrawWallet.as_view(), name='withdraw_wallet'),
    path('get-wallet/', GetWallet.as_view(), name='get_wallet'),
    path('wallet-history/', WalletHistoryView.as_view(), name='wallet-history'),
    path('challange-upgrade/', UpgradeChallangeView.as_view(),
         name='upgrade-challange'),
    path('get-challange/', GetChallangeView.as_view(), name='get-challange'),
    path('account-growth/', AccountGrowthView.as_view(), name='account-growth'),
]
