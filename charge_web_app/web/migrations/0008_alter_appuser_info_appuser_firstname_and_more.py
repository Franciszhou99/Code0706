# Generated by Django 4.0.4 on 2023-04-30 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0007_alter_appuser_info_appuser_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appuser_info',
            name='appuser_firstname',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='appuser_info',
            name='appuser_lastname',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='appuser_info',
            name='appuser_username',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
