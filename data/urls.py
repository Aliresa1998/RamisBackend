from django.urls import path
from .views import OhlcData, CryptoList, CreateTrade, Historytrade, UpdateHistoryTrade

urlpatterns = [
    path('data/', OhlcData.as_view(), name='data'),
    path('crypto_list/', CryptoList.as_view(), name='crypto_list'),
    path('trade/', CreateTrade.as_view(), name='create_trade'),
    path("history/", Historytrade.as_view(), name='history'),
    path("history/<int:pk>", UpdateHistoryTrade.as_view(), name='history')
]
