from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from web.models import card_info, vehicle, charge_pile, charge_order, charge_info, price_table, car_info, \
    charge_station_info, appuser_info, statement_info, price_type_info, dashboard_info, nation_info, operators_info


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    class Meta:
        model = User
        fields = '__all__'


    def create(self, validated_data):
        password = validated_data.pop('password')
        username = validated_data.pop('username')
        is_superuser = validated_data.pop('is_superuser')
        is_staff = validated_data.pop('is_staff')
        is_active = validated_data.pop('is_active')
        groups = validated_data.pop('groups')
        user_permissions = validated_data.pop('user_permissions')
        last_login = validated_data.pop('last_login')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        email = validated_data.pop('email')
        hashed_password = make_password(password)
        user = User.objects.create(username=username,password=hashed_password,is_superuser=is_superuser,
                                   is_staff=is_staff,is_active=is_active,email=email,last_login=last_login,
                                   first_name=first_name,last_name=last_name)
        user.user_permissions.set(user_permissions)
        user.groups.set(groups)
        return user

    def update(self, instance, validated_data):
        instance.is_superuser = validated_data.get('is_superuser', instance.is_superuser)
        instance.is_staff = validated_data.get('is_staff', instance.is_staff)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.last_login = validated_data.get('last_login', instance.last_login)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance

class appuser_info_serializer(serializers.ModelSerializer):
    class Meta:
        model = appuser_info
        fields = '__all__'

    def update(self,instance,validated_data):
        instance.appuser_username = validated_data.get('appuser_username', instance.appuser_username)
        instance.appuser_firstname = validated_data.get('appuser_firstname', instance.appuser_firstname)
        instance.appuser_lastname = validated_data.get('appuser_lastname', instance.appuser_lastname)
        instance.appuser_email = validated_data.get('appuser_email', instance.appuser_email)
        instance.appuser_phone_no = validated_data.get('appuser_phone_no', instance.appuser_phone_no)
        instance.appuser_postcode = validated_data.get('appuser_postcode', instance.appuser_postcode)
        instance.appuser_isactive = validated_data.get('appuser_isactive', instance.appuser_isactive)
        instance.appuser_address = validated_data.get('appuser_address',instance.appuser_address)
        instance.save()
        return instance

class charge_station_info_serializer(serializers.ModelSerializer):
    operators_id_fk = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = charge_station_info
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.station_name = validated_data.get('station_name', instance.station_name)
        instance.station_lat = validated_data.get('station_lat', instance.station_lat)
        instance.station_long = validated_data.get('station_long', instance.station_long)
        instance.station_location_state = validated_data.get('station_location_state', instance.station_location_state)
        instance.station_postcode = validated_data.get('station_postcode', instance.station_postcode)
        instance.save()
        return instance




class charge_info_serializer(serializers.ModelSerializer):
    class Meta:
        model = charge_info
        fields = '__all__'

class charge_pile_serializer(serializers.ModelSerializer):
    class Meta:
        model = charge_pile
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.pile_sn = validated_data.get('pile_sn', instance.pile_sn)
        instance.save()
        return instance


class charge_order_serializer(serializers.ModelSerializer):
    appuser_id_fk = appuser_info_serializer()
    pile_id_fk = charge_pile_serializer()
    charge_capacity_divided = serializers.SerializerMethodField()

    class Meta:
        model = charge_order
        fields = '__all__'

    def get_charge_capacity_divided(self, obj):
        if obj.charge_capacity is not None:
            return obj.charge_capacity / 1000


    def update(self, instance, validated_data):
        pile_data = validated_data.pop('pile_id_fk', {})
        appuser_data = validated_data.pop('appuser_id_fk', {})
        if pile_data:
            pile_info = instance.pile_id_fk
            pile_serializer = charge_pile_serializer(pile_info, data=pile_data)
            pile_serializer.is_valid(raise_exception=True)
            pile_serializer.save()
        if appuser_data:
            appuser_info = instance.appuser_id_fk
            appuser_serializer = appuser_info_serializer(appuser_info, data=appuser_data)
            appuser_serializer.is_valid(raise_exception=True)
            appuser_serializer.save()
        return super().update(instance, validated_data)


class price_table_serializer(serializers.ModelSerializer):
    station_id_fk = serializers.PrimaryKeyRelatedField(queryset=charge_station_info.objects.all())
    set_datetime = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = price_table
        fields = ['price_id','price_of_electricity','price_of_parking','set_datetime','station_id_fk']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['station_id_fk'] = charge_station_info_serializer(instance.station_id_fk).data
        return response


class vehicle_serializer(serializers.ModelSerializer):
    class Meta:
        model = vehicle
        fields = '__all__'
        read_only_field = ['veh_id']

    def update(self,instance,validated_data):
        instance.veh_brand = validated_data.get('veh_brand', instance.veh_brand)
        instance.veh_model = validated_data.get('veh_model', instance.veh_model)
        instance.veh_charge_type = validated_data.get('veh_charge_type', instance.veh_charge_type)
        instance.save()
        return instance

class car_info_serializer(serializers.ModelSerializer):
    veh_id_fk = vehicle_serializer()
    appuser_id_fk = appuser_info_serializer()

    class Meta:
        model = car_info
        fields = '__all__'
        read_only_field = ['car_id']

    def update(self,instance,validated_data):
        vehicle_data = validated_data.pop('veh_id_fk',{})
        appuser_data = validated_data.pop('appuser_id_fk',{})
        if vehicle_data:
            vehicle_info = instance.veh_id_fk
            vehicle_info_serilizer = vehicle_serializer(vehicle_info,data=vehicle_data)
            vehicle_info_serilizer.is_valid(raise_exception=True)
            vehicle_info_serilizer.save()
        if appuser_data:
            appuser_info = instance.appuser_id_fk
            appuser_serializer = appuser_info_serializer(appuser_info, data = appuser_data)
            appuser_serializer.is_valid(raise_exception=True)
            appuser_serializer.save()
        return super().update(instance,validated_data)


class statement_info_serializer(serializers.ModelSerializer):
    class Meta:
        model = statement_info
        fields = '__all__'


class price_type_info_serializer(serializers.ModelSerializer):
    class Meta:
        model = price_type_info
        fields = '__all__'


class dashboard_serializer(serializers.ModelSerializer):
    class Meta:
        model = dashboard_info
        fields = '__all__'

class card_info_serializer(serializers.ModelSerializer):
    class Meta:
        model = card_info
        fields = '__all__'

class nation_info_serializer(serializers.ModelSerializer):
    class Meta:
        model = nation_info
        fields = '__all__'

class operators_info_serializer(serializers.ModelSerializer):
    user_id_fk = UserSerializer()

    class Meta:
        model = operators_info
        fields = '__all__'

    def create(self, validated_data):
        nested_data = validated_data.pop('user_id_fk')
        nested_serilizer = UserSerializer(data = nested_data)
        if nested_serilizer.is_valid():
            nested_instance = nested_serilizer.save()
            validated_data['user_id_fk'] = nested_instance
        instance = super().create(validated_data)
        return instance


    def update(self,instance,validated_data):
        operators_data = validated_data.pop('user_id_fk',{})
        if operators_data:
            operators_info = instance.user_id_fk
            User_serializer = UserSerializer(operators_info,data=operators_data)
            User_serializer.is_valid(raise_exception=True)
            User_serializer.save()
        return super().update(instance,validated_data)