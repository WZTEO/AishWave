# Generated by Django 5.1.6 on 2025-03-05 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0024_task_alter_transaction_transaction_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billboardimage',
            name='image_url',
            field=models.ImageField(upload_to='uploads/'),
        ),
    ]
