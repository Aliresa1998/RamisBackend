# Generated by Django 4.2 on 2024-03-01 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0009_challange_status_wallet_todays_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='challange',
            name='changed_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
