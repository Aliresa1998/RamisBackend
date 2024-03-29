# Generated by Django 4.2 on 2024-03-01 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='duration',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='plan',
            name='target',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='plan',
            name='wallet_address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
