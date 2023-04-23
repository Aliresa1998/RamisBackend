from rest_framework import serializers
from .models import Crypto, Trade


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
        fields = ["user_id", "symbol", "direction", "amount", "entry_price", "exit_price", "stop_loss", "take_profit"]

    def create(self, validated_data):
        stop_loss = validated_data.get('stop_loss')
        take_profit = validated_data.get('take_profit')
        entry_price = validated_data.get('entry_price')
        direction = validated_data.get('direction')
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

    def save(self, *args, **kwargs):
        user_id = self.context['user']
        trade = Trade.objects.create(user=user_id, symbol=self.validated_data['symbol'],
                                     direction=self.validated_data['direction'],
                                     amount=self.validated_data['amount'],
                                     entry_price=self.validated_data['entry_price'],
                                     exit_price=self.validated_data['exit_price'],
                                     stop_loss=self.validated_data['stop_loss'],
                                     take_profit=self.validated_data['take_profit'])
        return trade
