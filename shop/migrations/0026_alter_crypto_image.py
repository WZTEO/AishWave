# Generated by Django 5.1.6 on 2025-07-01 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0025_alter_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crypto',
            name='image',
            field=models.URLField(blank=True, null=True),
        ),
    ]
