# Generated by Django 4.2 on 2024-02-21 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0006_rename_margin_trade_value_remove_trade_coin_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='trade',
            name='liquidation_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
    ]
