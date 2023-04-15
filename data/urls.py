from django.urls import path
from .views import OhlcData, CryptoList

urlpatterns = [
    path('data/', OhlcData.as_view(), name='data'),
    path('crypto_list/', CryptoList.as_view(), name='crypto_list')
]
