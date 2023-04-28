import decimal

from rest_framework.mixins import UpdateModelMixin, CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import DataSerializer, CryptoSerializer, TradeSerializer, HistorySerializer, WalletSerializer, \
    UpdateWalletSerializer
from .models import Crypto, Trade, Wallet, WalletHistory
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, GenericAPIView
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


class CreateWallet(CreateAPIView, UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WalletSerializer
        elif self.request.method == 'PUT':
            return UpdateWalletSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.request.user})
        return context

    def put(self, request, *args, **kwargs):
        wallet = Wallet.objects.get(user=self.request.user)
        balance = wallet.balance
        new_balance = self.request.data["balance"] + balance
        Wallet.objects.filter(user=self.request.user).update(balance=new_balance)
        wallet = Wallet.objects.get(user=self.request.user)
        res_data = UpdateWalletSerializer(wallet)
        WalletHistory.objects.create(user_id=self.request.user.id, transaction="DEPOSIT",
                                     amount=self.request.data["balance"])
        return Response(data=res_data.data, status=status.HTTP_200_OK)


class WithdrawWallet(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateWalletSerializer

    def put(self, request, *args, **kwargs):
        wallet = Wallet.objects.get(user=self.request.user).balance
        new_balance = wallet - self.request.data["balance"]
        if new_balance < 0:
            return Response("موجودی حساب شما کافی نیست .", status=status.HTTP_400_BAD_REQUEST)
        else:
            Wallet.objects.filter(user=self.request.user).update(balance=new_balance)
            wallet = Wallet.objects.get(user=self.request.user)
            res_data = UpdateWalletSerializer(wallet)
            WalletHistory.objects.create(user_id=self.request.user.id, transaction="WITHDRAW",
                                         amount=self.request.data["balance"])
            return Response(data=res_data.data, status=status.HTTP_200_OK)

