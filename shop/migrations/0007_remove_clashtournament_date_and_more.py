# Generated by Django 5.1.6 on 2025-06-18 06:09

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_alter_clashtournament_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clashtournament',
            name='date',
        ),
        migrations.RemoveField(
            model_name='clashtournament',
            name='time',
        ),
        migrations.AddField(
            model_name='clashtournament',
            name='datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
