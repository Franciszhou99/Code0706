# Generated by Django 4.1.1 on 2023-05-17 03:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0022_charge_pile_charge_price'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pile_schedule',
            old_name='weekly',
            new_name='rule_number',
        ),
    ]
