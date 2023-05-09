from rest_framework import serializers, status
from .models import AccountGrowth, Challange, Crypto, Trade, Wallet, WalletHistory
import yfinance as yf
from rest_framework.response import Response


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
        fields = ["user_id", "symbol", "direction", "amount", "stop_loss", "take_profit"]

    def create(self, validated_data):
        validated_data['user_id'] = self.context['user'].id
        try:
            validated_data['entry_price'] = yf.Ticker(validated_data["symbol"]).history()['Close'][-1]
        except:
            raise serializers.ValidationError("اسم ارز شما اشتباه است.")
        stop_loss = validated_data.get('stop_loss')
        take_profit = validated_data.get('take_profit')
        direction = validated_data.get('direction')
        entry_price = validated_data.get('entry_price')
        if stop_loss and stop_loss >= entry_price:
            raise serializers.ValidationError({'stop_loss': 'Stop loss price must be below entry price.'})
        if take_profit and take_profit <= entry_price:
            raise serializers.ValidationError({'take_profit': 'Take profit price must be above entry price.'})
        if direction == 'LONG' and stop_loss and take_profit and stop_loss >= take_profit:
            raise serializers.ValidationError(
                {'non_field_errors': 'For long trades, stop loss must be below take profit.'})
        if direction == 'SHORT' and stop_loss and take_profit and stop_loss <= take_profit:
            raise serializers.ValidationError(
                {'non_field_errors': 'For short trades, stop loss must be above take profit.'})

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
    class Meta:
        model = Challange
        fields = ['user_id', 'challange_level']

class AccountGrowthSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountGrowth
        fields = ['balance', 'date']