# Generated by Django 4.2 on 2024-02-21 17:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0005_trade_coin_amount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='trade',
            old_name='margin',
            new_name='value',
        ),
        migrations.RemoveField(
            model_name='trade',
            name='coin_amount',
        ),
    ]