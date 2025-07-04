# Generated by Django 5.1.6 on 2025-06-18 09:41

import django.db.models.deletion
import django_countries.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0008_remove_clashtournament_datetime_clashtournament_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BattleRoyaleTournament',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Battle royale tournament name', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='BattleRoyalePlayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('player_name', models.CharField(max_length=100)),
                ('kills', models.IntegerField(default=0)),
                ('matches_played', models.IntegerField(default=0)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='players', to='shop.battleroyaletournament')),
            ],
        ),
    ]
