from django.contrib.auth import get_user_model
import datetime
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
import datetime
from django.db import models


class charge_pile(models.Model):
    pile_status_choices = [
        ('Available','available'),
        ('Unavailable','unavailable'),
        ('Charging','charging')
    ]
    pile_loc_state_choices = [
        ('vic','VIC'),
        ('nsw','NSW'),
        ('tas','TAS'),
        ('qld','QLD'),
        ('wa','WA'),
        ('nt','NT'),
        ('act','ACT'),
        ('sa','SA')
    ]
    pile_id = models.AutoField(primary_key=True)
    pile_charge_type = models.CharField(max_length=255,blank=True)
    pile_lat = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    pile_long = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    pile_model = models.CharField(max_length=255,blank=True)
    pile_location_state = models.CharField(max_length=255,blank=True,null=True,choices=pile_loc_state_choices)
    pile_addres = models.CharField(max_length=255,blank=True,null=True)
    pile_status = models.CharField(max_length=255,blank=True,null=True,choices=pile_status_choices)
    pile_sn = models.CharField(max_length=255,blank=True)
    pile_vendor = models.CharField(max_length=255,blank=True)
    pile_metrfirmwareversion = models.CharField(max_length=255,blank=True)
    pile_ratekw = models.CharField(max_length=255,blank=True)
    pile_connect_no = models.IntegerField(blank=True)
    pile_outputcurrentmax = models.CharField(max_length=255,blank=True)
    charge_price = models.DecimalField(max_digits=10,decimal_places=6,blank=True,null=True,default=0.45)
    station_id_fk = models.ForeignKey('charge_station_info',models.DO_NOTHING,db_column='station_id_fk',blank=True,null=True)
    operators_id_fk = models.ForeignKey(get_user_model(), models.DO_NOTHING, db_column='operators_id_fk', blank=True,null=True)

class charge_info(models.Model):
    charge_id = models.AutoField(primary_key=True)
    connector_id = models.IntegerField(blank=True,null=True,default=1)
    charge_pile_id = models.ForeignKey('charge_pile', models.DO_NOTHING, db_column='charge_pile_id', blank=True,null=True)
    start_time = models.DateTimeField(blank=True)
    current = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    power = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    voltage = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    charge_capacity = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    meter_value = models.TextField(blank=True,null=False)
    transaction_id = models.BigIntegerField(blank=True)
    id_tag = models.CharField(max_length=255,blank=True,default='')
    appuser_id_fk = models.ForeignKey('appuser_info', models.DO_NOTHING, db_column='appuser_id_fk', blank=True,
                                      null=True)

class charge_order(models.Model):
    order_id = models.AutoField(primary_key=True)
    order_start_datetime = models.DateTimeField(blank=True,null=True)
    order_number = models.BigIntegerField(blank=True,null=True)
    pile_id_fk = models.ForeignKey('charge_pile', models.DO_NOTHING, db_column='pile_id_fk', blank=True, null=True)
    appuser_id_fk = models.ForeignKey('appuser_info', models.DO_NOTHING, db_column='appuser_id_fk', blank=True, null=True)
    order_end_datetime = models.DateTimeField(blank=True,null=True)
    order_fee = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    charge_capacity = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    order_status = models.CharField(max_length=255,blank=True,null=True,default='unpaid')
    paid_code = models.BigIntegerField(blank=True,null=True)
    paid_token = models.CharField(max_length=255, blank=True, null=True)
    GST = models.FloatField(default=0.1,blank=True,null=True)
    operators_id_fk = models.ForeignKey(get_user_model(),models.DO_NOTHING,db_column='operators_id_fk',blank=True,null=True)

class car_info(models.Model):
    car_id = models.AutoField(primary_key=True)
    car_registration_no = models.CharField(max_length=256,blank=True)
    register_datetime = models.DateTimeField(blank=True)
    veh_id_fk = models.ForeignKey('vehicle',models.DO_NOTHING, db_column='veh_id_fk', blank=True, null=True)
    appuser_id_fk = models.ForeignKey('appuser_info', models.DO_NOTHING, db_column='appuser_id_fk', blank=True, null=True)

class vehicle(models.Model):
    veh_id = models.AutoField(primary_key=True)
    veh_brand = models.CharField(max_length=255,blank=True)
    veh_model = models.CharField(max_length=255,blank=True)
    veh_charge_type = models.CharField(max_length=256,blank=True)

class charge_station_info(models.Model):
    station_id = models.AutoField(primary_key=True)
    station_name = models.CharField(max_length=255,blank=True,null=True)
    station_lat = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    station_long = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    station_location_state = models.CharField(max_length=255,blank=True,null=True)
    station_postcode = models.CharField(max_length=255,blank=True)
    operators_id_fk = models.ForeignKey(get_user_model(),models.DO_NOTHING,db_column='operators_id_fk',blank=True,null=True)


class price_table(models.Model):
    price_id = models.AutoField(primary_key=True)
    price_of_electricity = models.DecimalField(max_digits=10,decimal_places=6,blank=True,null=True)
    price_of_parking = models.DecimalField(max_digits=10,decimal_places=6,blank=True,null=True)
    set_datetime = models.DateTimeField(blank=True)
    station_id_fk = models.ForeignKey('charge_station_info',models.DO_NOTHING,db_column='station_id_fk',blank=True,null=True)


class appuser_info(models.Model):
    appuser_id = models.AutoField(primary_key=True)
    appuser_username = models.CharField(max_length = 255,blank=True,null=True)
    appuser_firstname = models.CharField(max_length=255,blank=True)
    appuser_lastname = models.CharField(max_length=255,blank=True)
    appuser_email = models.CharField(max_length=255,blank=True)
    appuser_phone_no = models.CharField(max_length=255,blank=True)
    appuser_postcode = models.CharField(max_length=30,blank=True,null=True)
    appuser_isactive = models.CharField(max_length=255,blank=True,null=True,default='active')
    appuser_password = models.CharField(max_length=255,blank=True)
    appuser_address = models.CharField(max_length=1800,blank=True,null=True)
    card_token = models.CharField(max_length=255,blank=True,null=True)
    last_login = models.DateTimeField(blank=True,null=True)
    register_datetime = models.DateTimeField(blank=True,null=True)
    token = models.CharField(verbose_name="TOKEN",max_length=64,null=True,blank=True)
    user_type = models.IntegerField(blank=True, null=True, default=0)


class statement_info(models.Model):
    statement_id = models.AutoField(primary_key=True)
    statement_datetime = models.DateTimeField(blank=True)
    operators_id_fk = models.ForeignKey(get_user_model(),models.DO_NOTHING,db_column='operators_id_fk',blank=True,null=True)
    statement_total_price = models.DecimalField(max_digits=10,decimal_places=4,blank=True,null=True)
    statement_charge_capacity = models.CharField(max_length=256,blank=True)

class price_type_info(models.Model):
    type_id = models.AutoField(primary_key=True)
    price_type = models.CharField(max_length=256,blank=True,null=True)

class dashboard_info(models.Model):
    dashboard_id = models.AutoField(primary_key=True)
    operators_id_fk = models.ForeignKey(get_user_model(),models.DO_NOTHING,db_column='operators_id_fk',blank=True,null=True)
    appuser_id_fk = models.ForeignKey('appuser_info', models.DO_NOTHING, db_column='appuser_id_fk', blank=True, null=True)

class card_info(models.Model):
    card_id = models.AutoField(primary_key=True)
    create_date = models.DateTimeField(blank=True,null=True)
    card_vendor = models.CharField(max_length=256,blank=True,null=True)
    card_number = models.BigIntegerField(blank=True,null=True)
    card_first_name = models.CharField(max_length=256,blank=True,null=True)
    card_last_name = models.CharField(max_length=256, blank=True, null=True)
    card_country = models.CharField(max_length=256, blank=True, null=True,default='Australia')
    user_card_token = models.CharField(max_length=256, blank=True, null=True)
    card_CVC = models.IntegerField(blank=True,null=True)
    expire_date_year = models.IntegerField(blank=True,null=True)
    expire_date_month = models.IntegerField(blank=True,null=True)
    appuser_id_fk = models.ForeignKey('appuser_info', models.DO_NOTHING, db_column='appuser_id_fk', blank=True, null=True)

class nation_info(models.Model):
    id = models.AutoField(primary_key=True)
    nation = models.CharField(max_length=255,blank=True,null=True)
    nation_number = models.CharField(max_length=255,blank=True,null=True)


class Cache(models.Model):
    cache_key = models.CharField(max_length=255, unique=True)
    value = models.TextField()
    expires = models.DateTimeField(db_index=True)

    class Meta:
        db_table = 'sms_cache_table'


class operators_info(models.Model):
    operators_id = models.AutoField(primary_key=True)
    user_id_fk = models.ForeignKey(get_user_model(), models.DO_NOTHING, db_column='user_id_fk', blank=True,null=True)
    operators_postcode = models.CharField(max_length=256,blank=True,null=True)
    operators_state = models.CharField(max_length=256,blank=True,null=True)

class pile_schedule(models.Model):
    id = models.AutoField(primary_key=True)
    rule_number = models.CharField(max_length=256,blank=True,null=True)
    start_time = models.TimeField(blank=True,null=True)
    end_time = models.TimeField(blank=True,null=True)
    charge_pile_fk = models.ForeignKey('charge_pile', models.DO_NOTHING, db_column='charge_pile_fk', blank=True,
                                      null=True)