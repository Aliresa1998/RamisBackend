from django.urls import path
from .views import OhlcData

urlpatterns = [
    path('data/', OhlcData.as_view(), name='data'),
]
