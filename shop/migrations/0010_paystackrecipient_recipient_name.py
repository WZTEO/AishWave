# Generated by Django 5.1.6 on 2025-02-28 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0009_alter_paystackrecipient_recipient_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='paystackrecipient',
            name='recipient_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
