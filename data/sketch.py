from django.utils import timezone
from .models import Trade, Order


def calculate_value(trade, price):
    initial_value = trade.amount * trade.entry_price * trade.leverage

    if trade.direction == 'LONG':
        new_value = trade.amount * price * trade.leverage
        # Check if stop_loss and take_profit are not None before comparing
        if trade.stop_loss is not None and price <= trade.stop_loss:
            trade.trade_status = 'CLOSED'
            trade.exit_price = trade.stop_loss
            trade.pnl = (trade.stop_loss - trade.entry_price) * trade.amount * trade.leverage
        elif trade.take_profit is not None and price >= trade.take_profit:
            trade.trade_status = 'CLOSED'
            trade.exit_price = trade.take_profit
            trade.pnl = (trade.take_profit - trade.entry_price) * trade.amount * trade.leverage

    elif trade.direction == 'SHORT':
        new_value = trade.amount * (2 * trade.entry_price - price) * trade.leverage
        # Check for stop loss and take profit for SHORT position
        if trade.stop_loss is not None and price >= trade.stop_loss:
            trade.trade_status = 'CLOSED'
            trade.exit_price = trade.stop_loss
            trade.pnl = (trade.entry_price - trade.stop_loss) * trade.amount * trade.leverage
        elif trade.take_profit is not None and price <= trade.take_profit:
            trade.trade_status = 'CLOSED'
            trade.exit_price = trade.take_profit
            trade.pnl = (trade.entry_price - trade.take_profit) * trade.amount * trade.leverage

    # Check for liquidation
    if initial_value - new_value >= trade.liquidation_amount:
        trade.trade_status = 'Liquidated'
        trade.exit_price = price
    elif trade.trade_status == 'CLOSED':
        trade.value = trade.exit_price * trade.amount * trade.leverage
    elif trade.trade_status == 'Open':
        trade.value = new_value
    # Save changes to the database
    trade.save(update_fields=['value', 'trade_status', 'exit_price', 'pnl'])


def update_order(order, current_price):
    if not order.is_done and not order.is_delete:
        if order.order_type == 'BUY_LIMIT' and current_price <= order.price:
            order.is_done = True
        elif order.order_type == 'SELL_LIMIT' and current_price >= order.price:
            order.is_done = True
        elif order.order_type == 'BUY_STOP' and current_price >= order.price:
            order.is_done = True
        elif order.order_type == 'SELL_STOP' and current_price <= order.price:
            order.is_done = True
        order.save()


def update_trades(symbol, price):
    trades = Trade.objects.filter(symbol=symbol, trade_status='OPEN')
    for trade in trades:
        calculate_value(trade, price)

    orders = Order.objects.filter(symbol=symbol, is_done=False, is_delete=False)
    for order in orders:
        update_order(order, price)