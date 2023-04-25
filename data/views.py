import decimal

from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import DataSerializer, CryptoSerializer, TradeSerializer, HistorySerializer
from .models import Crypto, Trade
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView
from datetime import datetime
import yfinance as yf
import time


# Create your views here.
class OhlcData(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = DataSerializer

    def post(self, request, *args, **kwargs):
        """
           A view that get data Financial market .

           Parameters:
                 name (string): currency name.
                 interval (string): currency interval.
                 period (string) : currency period.
        """
        try:
            name = self.request.data['name']
            try:
                interval = self.request.data['interval']
            except KeyError:
                interval = "1h"
            try:
                period = self.request.data['period']
            except KeyError:
                period = "24h"
            data = yf.download(tickers=f'{name}', period=f'{period}', interval=f'{interval}')
            result = data.to_json(orient="records")
        except:
            return Response("Enter your currency name .", status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK, data=result)


class CryptoList(ListAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = CryptoSerializer
    queryset = Crypto.objects.all()


class CreateTrade(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TradeSerializer

    def get_serializer_context(self):
        return {"user": self.request.user}


class Historytrade(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HistorySerializer

    def get_queryset(self):
        return Trade.objects.filter(user=self.request.user)


class UpdateHistoryTrade(UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        try:
            pk = kwargs['pk']
        except KeyError:
            return Response('کلید اصلی شما اشتباه است.', status=status.HTTP_400_BAD_REQUEST)
        symbol = Trade.objects.get(id=pk)
        exit_price = yf.Ticker(symbol.symbol).history()['Close'][-1]
        exit_price = decimal.Decimal(exit_price)
        trade = Trade.objects.get(pk=pk)
        pnl = (exit_price - trade.entry_price) * trade.amount
        Trade.objects.filter(pk=pk).update(pnl=pnl, status=False, exit_price=exit_price, close_time=datetime.now())
        return Response("موفقیت آمیز بود.", status=status.HTTP_200_OK)