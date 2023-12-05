# Generated by Django 4.1.1 on 2023-06-05 07:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('web', '0037_appuser_info_user_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operators_info',
            name='user_id_fk',
            field=models.ForeignKey(blank=True, db_column='user_id_fk', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
    ]
