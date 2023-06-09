import decimal
from datetime import datetime
import yfinance as yf
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .serializers import AccountGrowthSerializer, DataSerializer, CryptoSerializer, TradeSerializer, HistorySerializer, WalletHistorySerializer, ChallangeSerializer, \
    UpdateWalletSerializer, GetWalletSerializer, WithdrawSerializer
from .models import AccountGrowth, Challange, Crypto, Trade, Wallet, WalletHistory

from users.permissions import AdminAccessPermission
from users.pagination import CustomPagination

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
            data = yf.download(
                tickers=f'{name}', period=f'{period}', interval=f'{interval}')
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
    pagination_class = CustomPagination

    def get_queryset(self):
        if self.kwargs['type'] == 'short':
            return Trade.objects.filter(user=self.request.user).filter(direction='SHORT').all()
        elif self.kwargs['type'] == 'long':
            return Trade.objects.filter(user=self.request.user).filter(direction='LONG').all()
        elif self.kwargs['type'] == 'all':
            return Trade.objects.filter(user=self.request.user).all()


class UpdateHistoryTrade(UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        try:
            pk = kwargs['pk']
        except KeyError:
            return Response('کلید اصلی شما اشتباه است.', status=status.HTTP_400_BAD_REQUEST)
        wallet_balance = Wallet.objects.get(user=self.request.user).balance
        symbol = Trade.objects.get(id=pk)
        exit_price = yf.Ticker(symbol.symbol).history()['Close'][-1]
        exit_price = decimal.Decimal(exit_price)
        trade = Trade.objects.get(pk=pk)
        pnl = (exit_price - trade.entry_price) * trade.amount
        Trade.objects.filter(pk=pk).update(
            pnl=pnl, status=False, exit_price=exit_price, close_time=datetime.now())
        new_wallet_balance = wallet_balance + (exit_price*trade.amount)
        Wallet.objects.filter(user=self.request.user).update(
            balance=new_wallet_balance)
        return Response("موفقیت آمیز بود.", status=status.HTTP_200_OK)


class CreateWallet(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateWalletSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.request.user})
        return context

    def put(self, request, *args, **kwargs):
        (wallet, created) = Wallet.objects.get_or_create(user=self.request.user)
        balance = wallet.balance
        new_balance = self.request.data["balance"] + balance
        Wallet.objects.filter(user=self.request.user).update(
            balance=new_balance)
        (wallet, created) = Wallet.objects.get_or_create(user=self.request.user)
        res_data = UpdateWalletSerializer(wallet)
        WalletHistory.objects.create(user_id=self.request.user.id, transaction="DEPOSIT",
                                     amount=self.request.data["balance"])
        return Response(data=res_data.data, status=status.HTTP_200_OK)


class WithdrawWallet(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WithdrawSerializer

    def put(self, request, *args, **kwargs):
        wallet = Wallet.objects.get(user=self.request.user).balance
        new_balance = wallet - self.request.data["balance"]
        if new_balance < 0:
            return Response("موجودی حساب شما کافی نیست .", status=status.HTTP_400_BAD_REQUEST)
        else:
            Wallet.objects.filter(user=self.request.user).update(
                balance=new_balance)
            (wallet, created) = Wallet.objects.get_or_create(
                user=self.request.user)
            res_data = UpdateWalletSerializer(wallet)
            WalletHistory.objects.create(user_id=self.request.user.id, transaction="WITHDRAW",
                                         amount=self.request.data["balance"], wallet_destination=self.request.data['widthdraw_destination'])
            return Response(data=res_data.data, status=status.HTTP_200_OK)


class GetWallet(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetWalletSerializer

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    def get_object(self):
        (wallet, created) = Wallet.objects.get_or_create(user=self.request.user)
        return wallet


class WalletHistoryView(ListAPIView):
    serializer_class = WalletHistorySerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return WalletHistory.objects.filter(user=self.request.user)


class UpgradeChallangeView(UpdateAPIView):
    permission_classes = [AdminAccessPermission]
    serializer_class = ChallangeSerializer

    def put(self, request, *args, **kwargs):
        Challange.objects.filter(user=self.request.data['user']).update(
            challange_level=self.request.data['challange_level'])
        account = Challange.objects.get(user=self.request.data['user'])
        res = ChallangeSerializer(account)
        return Response(data=res.data, status=status.HTTP_200_OK)


class GetChallangeView(ListAPIView):
    serializer_class = ChallangeSerializer

    def get_queryset(self):
        current_user = self.request.user
        (wallet, created) = Wallet.objects.get_or_create(user=current_user)
        user_balance = wallet.balance
        if user_balance <= 500:
            Challange.objects.filter(
                user=current_user).update(challange_level='1')
        elif 500 < user_balance <= 5000:
            Challange.objects.filter(
                user=current_user).update(challange_level='2')
        elif user_balance >= 500:
            Challange.objects.filter(
                user=current_user).update(challange_level='3')
        return Challange.objects.filter(user=self.request.user).all()


class AccountGrowthView(ListAPIView):
    serializer_class = AccountGrowthSerializer

    def get_queryset(self):
        AccountGrowth.objects.filter(user=self.request.user).all()


