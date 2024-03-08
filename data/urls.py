from django.urls import path
from .views import (
    AccountGrowthView, GetChallangeView, UpgradeChallangeView, 
    OhlcData, CryptoList, CreateTrade, Historytrade, UpdateHistoryTrade, 
    CreateWallet, WalletHistoryView, WithdrawWallet, GetWallet, PlaceOrderView, 
    GetOrder, DeleteOrder, CloseHistoryTrade, GetAllCoins, ListWalletSnapShot,
    UserDeposit, UserSummary)

urlpatterns = [
    path('data/', OhlcData.as_view(), name='data'),
    path('crypto_list/', CryptoList.as_view(), name='crypto_list'),
    path('trade/', CreateTrade.as_view(), name='create_trade'),
    path("history/<str:type>", Historytrade.as_view(), name='history'),
    path("close/<int:pk>/", CloseHistoryTrade.as_view(), name='history_without_leverage'),
    path("deposit-wallet/", CreateWallet.as_view(), name='wallet'),
    path("withdraw/", WithdrawWallet.as_view(), name='withdraw_wallet'),
    path('get-wallet/', GetWallet.as_view(), name='get_wallet'),
    path('wallet-history/', WalletHistoryView.as_view(), name='wallet-history'),
    path('challange-upgrade/', UpgradeChallangeView.as_view(),
         name='upgrade-challange'),
    path('get-challange/', GetChallangeView.as_view(), name='get-challange'),
    path('account-growth/', AccountGrowthView.as_view(), name='account-growth'),
    path('place-order/', PlaceOrderView.as_view(), name='place-order'),
    path('get-order/', GetOrder.as_view(), name='get-order'),
    path('delete-order/<int:order_id>', DeleteOrder.as_view(), name='delete'),
    path("update/<int:pk>/", UpdateHistoryTrade.as_view(), name=''),
    path('get-all-coins/', GetAllCoins.as_view(), name='get-all-coins'),
    path('wallet-snapshot-list/', ListWalletSnapShot.as_view(), name='wallet-snapshot-list'),
    path('user-deposit/', UserDeposit.as_view(), name='user-deposit'),
    path('user-summary/<int:pk>/', UserSummary.as_view())
]
