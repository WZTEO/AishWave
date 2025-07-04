# Generated by Django 5.1.1 on 2025-06-18 08:47

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_remove_clashtournament_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clashtournament',
            name='datetime',
        ),
        migrations.AddField(
            model_name='clashtournament',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='clashtournament',
            name='time',
            field=models.IntegerField(default=0, help_text='Enter time as HHMM, e.g., 1330 for 1:30 PM'),
        ),
    ]
