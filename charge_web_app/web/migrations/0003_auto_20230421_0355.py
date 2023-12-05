# Generated by Django 3.2.18 on 2023-04-21 03:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_auto_20230419_0626'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appuser_info',
            name='appuser_address',
            field=models.CharField(blank=True, max_length=1800),
        ),
        migrations.AlterField(
            model_name='appuser_info',
            name='appuser_isactive',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='appuser_info',
            name='appuser_phone_no',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='car_info',
            name='car_registration_no',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AlterField(
            model_name='car_info',
            name='register_datetime',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='charge_info',
            name='id_tag',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='charge_info',
            name='meter_value',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='charge_info',
            name='start_time',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='charge_order',
            name='GST',
            field=models.FloatField(blank=True, default=1),
        ),
        migrations.AlterField(
            model_name='charge_order',
            name='charge_capacity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='charge_order',
            name='order_end_datetime',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='charge_order',
            name='order_fee',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='charge_order',
            name='order_start_datetime',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='charge_pile',
            name='pile_charge_type',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='charge_pile',
            name='pile_connect_no',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='charge_pile',
            name='pile_metrfirmwareversion',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='charge_pile',
            name='pile_model',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='charge_pile',
            name='pile_outputcurrentmax',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='charge_pile',
            name='pile_ratekw',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='charge_pile',
            name='pile_sn',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='charge_pile',
            name='pile_vendor',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='charge_station_info',
            name='station_postcode',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='price_table',
            name='set_datetime',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='statement_info',
            name='statement_charge_capacity',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AlterField(
            model_name='statement_info',
            name='statement_datetime',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='veh_brand',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='veh_charge_type',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='veh_model',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.CreateModel(
            name='card_info',
            fields=[
                ('card_id', models.AutoField(primary_key=True, serialize=False)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('card_number', models.IntegerField(blank=True, null=True)),
                ('expire_date', models.CharField(blank=True, max_length=256, null=True)),
                ('security_code', models.IntegerField(blank=True, null=True)),
                ('appuser_id_fk', models.ForeignKey(blank=True, db_column='appuser_id_fk', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='web.appuser_info')),
            ],
        ),
    ]
