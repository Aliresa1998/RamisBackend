import decimal
from rest_framework import serializers, status
from .models import (
    AccountGrowth, Challange, Crypto, Trade, Wallet, WalletHistory, 
    Order, WalletSnapShot
    )
import yfinance as yf
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone


class DataSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=250)
    interval = serializers.CharField(max_length=250)
    period = serializers.CharField(max_length=250)


class CryptoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crypto
        fields = ("name", "image_url",)


class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = ["leverage", "user_id", "symbol", "direction",
                  "amount", "stop_loss", "take_profit"]

    def create(self, validated_data):
        validated_data['user_id'] = self.context['user'].id
        try:
            validated_data['entry_price'] = yf.Ticker(
                validated_data["symbol"]).history()['Close'][-1]
        except:
            raise serializers.ValidationError("اسم ارز شما اشتباه است.")
        stop_loss = validated_data.get('stop_loss')
        take_profit = validated_data.get('take_profit')
        direction = validated_data.get('direction')
        entry_price = validated_data.get('entry_price')
        total_cost = validated_data.get(
            'amount') * decimal.Decimal(validated_data.get('entry_price'))
        wallet = Wallet.objects.get(user=self.context['user'])
        wallet_balance = wallet.balance
        if wallet_balance - total_cost < 0:
            raise serializers.ValidationError('موجودی شما کافی نمیباشد')
        else:
            if stop_loss == 0 or take_profit == 0:
                raise serializers.ValidationError(
                    "مقدار توقف ضرر یا مقدار حد سود نمیتواند صفر باشد . ")
            if direction == 'LONG' and stop_loss and stop_loss >= entry_price:
                raise serializers.ValidationError(
                    {'stop_loss': ' . قیمت توقف ضرر باید کمتر از مقدار ورودی باشد'})
            if direction == 'LONG' and take_profit and take_profit <= entry_price:
                raise serializers.ValidationError(
                    {'take_profit': ' . قیمت سود باید بالاتر از قیمت ورودی باشد '})
            if direction == 'SHORT' and stop_loss and stop_loss <= entry_price:
                raise serializers.ValidationError(
                    {'stop_loss': 'قیمت توقف ضرر باید بالاتر از قیمت ورودی باشد .'})
            if direction == 'SHORT' and take_profit and take_profit >= entry_price:
                raise serializers.ValidationError(
                    {'take_profit': 'قیمت سود باید کمتر از قیمت ورودی باشد .'})
            if direction == 'LONG' and stop_loss and take_profit and stop_loss >= take_profit:
                raise serializers.ValidationError(
                    {'non_field_errors': 'For long trades, stop loss must be below take profit.'})
            if direction == 'SHORT' and stop_loss and take_profit and stop_loss <= take_profit:
                raise serializers.ValidationError(
                    {'non_field_errors': 'For short trades, stop loss must be above take profit.'})
            wallet.balance = wallet_balance - total_cost
            wallet.save()
            return super().create(validated_data)


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = "__all__"


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["user_id", "balance"]

    def create(self, validated_data):
        validated_data['user_id'] = self.context['user'].id
        WalletHistory.objects.create(user_id=validated_data['user_id'], transaction="DEPOSIT",
                                     amount=validated_data["balance"])
        return super().create(validated_data)


class UpdateWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["user_id", "balance"]


class GetWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'


class WithdrawSerializer(serializers.ModelSerializer):
    widthdraw_destination = serializers.CharField()

    class Meta:
        model = Wallet
        fields = ["user_id", "balance", 'widthdraw_destination']


class WalletHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletHistory
        fields = '__all__'


class ChallangeSerializer(serializers.ModelSerializer):
    growth = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()


    class Meta:
        model = Challange
        fields = [
            'user', 'challange_level', 'growth', 'total_assets', 'start_day_assets',
            'days_remaining']
    
    def get_growth(self, obj):
        if obj.start_day_assets == 0:  # Avoid division by zero
            return None
        growth = ((obj.total_assets - obj.start_day_assets) / obj.start_day_assets) * 100
        return f'{growth:.2f}%'

    def get_days_remaining(self, obj):
        if obj.challange_level == '1':
            end_date = obj.created_at + timedelta(days=30)
        elif obj.challange_level == '2':
            if obj.changed_date:
                end_date = obj.changed_date + timedelta(days=60)
            else:  # Fallback if changed_date is somehow not set
                end_date = obj.created_at + timedelta(days=60)
        else:  # For level 3
            return "Unlimited"
        
        days_remaining = (end_date - timezone.now()).days
        return days_remaining if days_remaining > 0 else 0

class AccountGrowthSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountGrowth
        fields = ['balance', 'date']


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ["id", 'user', 'order_type', 'price', 'amount', 'symbol', "is_delete"]


class WalletSnapShotListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletSnapShot
        fields = ['balance', 'created']