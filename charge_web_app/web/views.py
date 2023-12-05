import json
import os
import random
import requests
from _decimal import Decimal
from django.http import FileResponse, HttpResponse
from django.utils import timezone
from django.middleware.csrf import get_token
from django.db.models import Q
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, filters
import django_filters
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import vehicle, charge_pile, charge_info, charge_order, price_table, car_info, \
    charge_station_info, appuser_info, statement_info, price_type_info, operators_info
from .serializers import vehicle_serializer, charge_pile_serializer, charge_order_serializer, price_table_serializer, car_info_serializer, \
    charge_station_info_serializer, appuser_info_serializer, statement_info_serializer, price_type_info_serializer, \
    operators_info_serializer

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from datetime import date, timedelta
import datetime
from django.db.models import Sum
import pytz
from .statement_generate import Graphs

from reportlab.platypus import SimpleDocTemplate, Spacer, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

account_sid = 'ACc1028bbc8e296c74ee480b064c9f5faf'
auth_token = '9ce67e1b193deb1ad64c44b7d024ebb0'
phone = '+61483927788'
local_tz = timezone.get_current_timezone()

class PageNum(PageNumberPagination):
    page_size = 10


# Management Platform User Login Function
class LoginView(APIView):
    def get(self,request):
        crsf_token = get_token(request)
        if crsf_token:
            return Response({'code':200,'crsf_token':crsf_token,'message':'successful get token!'})
        else:
            return Response({'code':201,'data': {},'message':'Error'})

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            token,_= Token.objects.get_or_create(user=user)
            userid = Token.objects.filter(key=token).values("user_id")
            # userid = userid[0]['user_id']
            # print(user_id[0]['user_id'])
            super_user = User.objects.filter(id= userid[0]['user_id']).values('is_superuser')
            station_id = charge_station_info.objects.filter(operators_id_fk=userid[0]['user_id']).values('station_id')
            return Response({'code':200,'data':{'token':token.key,'is_superuser':super_user[0]['is_superuser'],'station_id':station_id},'message': 'Login successfully.'})
        else:
            return Response({'code':201,'data':{},'error':'Invalid username or password'},status=status.HTTP_400_BAD_REQUEST)


# Management System User Logout
class LogoutView(APIView):
    def post(self,request):
        authtoken = request.data.get('auth_token')
        token = Token.objects.filter(key = authtoken)
        #logout(request)
        if token:
            token.delete()
            request.session.flush()
            return Response({'code':200,'data':{},'message':'You have been successfully logged out.'})
        else:
            return Response({'code':201,'data':{},'message':'You already log out!'})

# Dashboard platform showing informtaion
class DashboardView(APIView):
    # post chart information
    def post(self,request):
        operator_token = request.headers.get('Token')
        datetime_choice = request.GET.get('datetime_choice')
        operator_id  = Token.objects.filter(key = operator_token).values("user_id")
        if operator_id:
            operator_id = operator_id[0]['user_id']
            if datetime_choice == 'hour':
                target_timezone = pytz.timezone('Australia/Melbourne')
                now_day = datetime.datetime.now(target_timezone).replace(tzinfo=None)
                data_hourly = now_day - timedelta(hours=1)
                carb_data_capacity_hour = charge_order.objects.filter(order_end_datetime__gte=data_hourly,order_end_datetime__lte=now_day,operators_id_fk=operator_id).values('order_end_datetime','charge_capacity')
                #data_capacity_hour = charge_order.objects.filter(order_end_datetime__gte=data_hourly,order_end_datetime__lte=now_day).aggregate(nums=Sum('charge_capacity'))
                #carbon_capacity = float(data_capacity_hour['nums'] / 1000) * 0.785
                if carb_data_capacity_hour:
                    for items in carb_data_capacity_hour:
                        items['charge_capacity'] = float(items['charge_capacity']/1000) * 0.785
                data_fee_hour = charge_order.objects.filter(order_end_datetime__gte=data_hourly,order_end_datetime__lte=now_day,operators_id_fk=operator_id).values('order_end_datetime','order_fee')
                data_capacity_hour = charge_order.objects.filter(order_end_datetime__gte=data_hourly,order_end_datetime__lte=now_day,operators_id_fk=operator_id).values('order_end_datetime','charge_capacity')
                return Response({'code':200,'data':{'datafeehour':data_fee_hour,'datacapacityhour':data_capacity_hour,'carbdatacapacityhour':carb_data_capacity_hour},'message':'get information successful!'})
            elif datetime_choice == 'day':
                data_fortoday = date.today()
                carb_data_capacity_today = charge_order.objects.filter(order_end_datetime__year=data_fortoday.year,order_end_datetime__month=data_fortoday.month,order_end_datetime__day=data_fortoday.day,operators_id_fk=operator_id).values('order_end_datetime', 'charge_capacity')
                # data_capacity_today = charge_order.objects.filter(order_end_datetime__year=data_fortoday.year,order_end_datetime__month=data_fortoday.month,order_end_datetime__day=data_fortoday.day).aggregate(nums=Sum('charge_capacity'))
                # carbon_capacity = float(data_capacity_today['nums'] / 1000) * 0.785
                if carb_data_capacity_today:
                    for items in carb_data_capacity_today:
                        items['charge_capacity'] = float(items['charge_capacity'] / 1000) * 0.785
                data_fee_today = charge_order.objects.filter(order_end_datetime__year=data_fortoday.year,order_end_datetime__month=data_fortoday.month,order_end_datetime__day=data_fortoday.day,operators_id_fk=operator_id).values('order_end_datetime','order_fee')
                data_capacity_today = charge_order.objects.filter(order_end_datetime__year=data_fortoday.year,order_end_datetime__month=data_fortoday.month,order_end_datetime__day=data_fortoday.day,operators_id_fk=operator_id).values('order_end_datetime','charge_capacity')
                return Response({'code':200,'data':{'datafeetoday':data_fee_today,'datacapacitytoday':data_capacity_today,'carbdatacapacitytoday':carb_data_capacity_today},'message':'get information successful'})
            elif datetime_choice == 'month':
                data_fortoday = date.today()
                carb_data_capacity_month = charge_order.objects.filter(order_end_datetime__year=data_fortoday.year,order_end_datetime__month=data_fortoday.month,operators_id_fk=operator_id).values('order_end_datetime', 'charge_capacity')
                if carb_data_capacity_month:
                    for items in carb_data_capacity_month:
                        items['charge_capacity'] = float(items['charge_capacity'] / 1000) * 0.785
                data_fee_month = charge_order.objects.filter(order_end_datetime__year=data_fortoday.year,order_end_datetime__month=data_fortoday.month,operators_id_fk=operator_id).values('order_end_datetime','order_fee')
                data_capacity_month = charge_order.objects.filter(order_end_datetime__year=data_fortoday.year,order_end_datetime__month=data_fortoday.month,operators_id_fk=operator_id).values('order_end_datetime','charge_capacity')
                return Response({'code':200,'data':{'datafeemonth':data_fee_month,'datacapcitymonth':data_capacity_month,'carbdatacapcitymonth':carb_data_capacity_month},'message':'get information successful!'})
        return Response({'code':201,'data':{},'error':'Can not find data!'})

    def get(self,request):
        # get yesterday date
        operator_token = request.headers.get('Token')
        operator_id = Token.objects.filter(key=operator_token).values("user_id")
        if operator_id:
            operator_id = operator_id[0]['user_id']
            superuser = User.objects.filter(id=operator_id).values('is_superuser')
            now_day = date.today()
            yesterday = now_day - timedelta(days=1)
            year = now_day.year
            month = now_day.month
            if superuser[0]['is_superuser']:
                data_order_fee_year = charge_order.objects.filter(order_end_datetime__year=year).aggregate(nums=Sum('order_fee'))
                if data_order_fee_year['nums'] != 0 and data_order_fee_year['nums'] != None:
                    data_order_fee_year = data_order_fee_year['nums']
                else:
                    data_order_fee_year = 0
                data_order_fee_month = charge_order.objects.filter(order_end_datetime__year=year,order_end_datetime__month=month).aggregate(nums=Sum('order_fee'))
                if data_order_fee_month['nums'] != 0 and data_order_fee_month['nums'] != None:
                    data_order_fee_month = data_order_fee_month['nums']
                else:
                    data_order_fee_month = 0
                data_order_fee_yesterday = charge_order.objects.filter(order_end_datetime=yesterday).aggregate(nums=Sum('order_fee'))
                if data_order_fee_yesterday['nums'] != 0 and data_order_fee_yesterday['nums'] != None:
                    data_order_fee_yesterday = data_order_fee_yesterday['nums']
                else:
                    data_order_fee_yesterday = 0
                data_order_capacity_year = charge_order.objects.filter(order_end_datetime__year=year).aggregate(nums=Sum('charge_capacity'))
                data_order_capacity_month = charge_order.objects.filter(order_end_datetime__year=year,order_end_datetime__month=month).aggregate(nums=Sum('charge_capacity'))
                data_order_capacity_yesterday = charge_order.objects.filter(order_end_datetime=yesterday).aggregate(nums=Sum('charge_capacity'))
                if data_order_capacity_year['nums'] != 0 and data_order_capacity_year['nums'] != None:
                        data_order_capacity_year = data_order_capacity_year['nums']/1000
                else:
                    data_order_capacity_year = 0
                if data_order_capacity_month['nums'] != 0 and data_order_capacity_month['nums'] != None:
                    data_order_capacity_month = data_order_capacity_month['nums']/1000
                else:
                    data_order_capacity_month = 0
                if data_order_capacity_yesterday['nums'] != 0 and data_order_capacity_yesterday['nums'] != None:
                    data_order_capacity_yesterday = data_order_capacity_yesterday['nums']/1000
                else:
                    data_order_capacity_yesterday = 0
                total_charge_station = charge_station_info.objects.filter().count()
                # station_id = charge_station_info.objects.filter(operators_id_fk=operator_id).values('station_id')
                total_charge_pile = charge_pile.objects.filter()
                unique_charge_pile = set()
                for obj in total_charge_pile:
                    field_val = obj.pile_sn
                    unique_charge_pile.add(field_val)
                total_charge_pile_no = len(unique_charge_pile)
                total_charge_pile_connect_no = charge_pile.objects.all().count()
                total_charge_pile_av = charge_pile.objects.filter(pile_status='Available').count()
                total_charge_pile_unav = charge_pile.objects.filter(pile_status='Unavailable').count()
                total_charge_pile_charging = charge_pile.objects.filter(pile_status='Charging').count()
                return Response({'code':200,'data':{'data_order_fee':{'data_order_fee_year': data_order_fee_year,'data_order_fee_month':data_order_fee_month,'data_order_fee_yesterday':data_order_fee_yesterday},'data_order_capacity':{'data_order_capacity_year':data_order_capacity_year,'data_order_capacity_month':data_order_capacity_month,'data_order_capacity_yesterday':data_order_capacity_yesterday},'total_data':{'total_charge_station':total_charge_station,'total_charge_pile':total_charge_pile_no,'total_charge_pile_connect_no':total_charge_pile_connect_no},'charge_pile_status':{'total_avaliable_pile':total_charge_pile_av,'total_unavaliable_pile':total_charge_pile_unav,'total_charging_pile':total_charge_pile_charging}}})
            else:
                data_order_fee_year = charge_order.objects.filter(order_end_datetime__year = year, operators_id_fk=operator_id ).aggregate(nums=Sum('order_fee'))
                if data_order_fee_year['nums'] != 0 and data_order_fee_year['nums'] != None:
                    data_order_fee_year = data_order_fee_year['nums']
                else:
                    data_order_fee_year = 0
                data_order_fee_month = charge_order.objects.filter(order_end_datetime__year = year,order_end_datetime__month=month, operators_id_fk=operator_id).aggregate(nums=Sum('order_fee'))
                if data_order_fee_month['nums'] != 0 and data_order_fee_month['nums'] != None:
                    data_order_fee_month = data_order_fee_month['nums']
                else:
                    data_order_fee_month = 0
                data_order_fee_yesterday = charge_order.objects.filter(order_end_datetime = yesterday, operators_id_fk=operator_id).aggregate(nums=Sum('order_fee'))
                if data_order_fee_yesterday['nums'] != 0 and data_order_fee_yesterday['nums'] != None:
                    data_order_fee_yesterday = data_order_fee_yesterday['nums']
                else:
                    data_order_fee_yesterday = 0
                data_order_capacity_year = charge_order.objects.filter(order_end_datetime__year=year, operators_id_fk=operator_id).aggregate(nums=Sum('charge_capacity'))
                data_order_capacity_month = charge_order.objects.filter(order_end_datetime__year=year,order_end_datetime__month=month,operators_id_fk=operator_id).aggregate(nums=Sum('charge_capacity'))
                data_order_capacity_yesterday = charge_order.objects.filter(order_end_datetime = yesterday, operators_id_fk=operator_id).aggregate(nums=Sum('charge_capacity'))
                if data_order_capacity_year['nums'] != 0 and data_order_capacity_year['nums'] != None:
                        data_order_capacity_year = data_order_capacity_year['nums']/1000
                else:
                    data_order_capacity_year = 0
                if data_order_capacity_month['nums'] != 0 and data_order_capacity_month['nums'] != None:
                    data_order_capacity_month = data_order_capacity_month['nums']/1000
                else:
                    data_order_capacity_month = 0
                if data_order_capacity_yesterday['nums'] != 0 and data_order_capacity_yesterday['nums'] != None:
                    data_order_capacity_yesterday = data_order_capacity_yesterday['nums']/1000
                else:
                    data_order_capacity_yesterday = 0
                total_charge_station = charge_station_info.objects.filter(operators_id_fk=operator_id).count()
                # station_id = charge_station_info.objects.filter(operators_id_fk=operator_id).values('station_id')
                total_charge_pile = charge_pile.objects.filter(operators_id_fk=operator_id)
                unique_charge_pile = set()
                for obj in total_charge_pile:
                    field_val = obj.pile_sn
                    unique_charge_pile.add(field_val)
                total_charge_pile_no = len(unique_charge_pile)
                total_charge_pile_connect_no = charge_pile.objects.all().count()
                total_charge_pile_av = charge_pile.objects.filter(pile_status='Available', operators_id_fk=operator_id).count()
                total_charge_pile_unav = charge_pile.objects.filter(pile_status='Unavailable', operators_id_fk=operator_id).count()
                total_charge_pile_charging = charge_pile.objects.filter(pile_status='Charging', operators_id_fk=operator_id).count()
                return Response({'code':200,'data':{'data_order_fee':{'data_order_fee_year': data_order_fee_year,'data_order_fee_month':data_order_fee_month,'data_order_fee_yesterday':data_order_fee_yesterday},'data_order_capacity':{'data_order_capacity_year':data_order_capacity_year,'data_order_capacity_month':data_order_capacity_month,'data_order_capacity_yesterday':data_order_capacity_yesterday},'total_data':{'total_charge_station':total_charge_station,'total_charge_pile':total_charge_pile_no,'total_charge_pile_connect_no':total_charge_pile_connect_no},'charge_pile_status':{'total_avaliable_pile':total_charge_pile_av,'total_unavaliable_pile':total_charge_pile_unav,'total_charging_pile':total_charge_pile_charging}}})
        else:
            return Response({'code':201,'data':{},'message':'error can not find operators info!'})


# App user & Web user get real time charge management
class ChargeInfoView(APIView):
    def post(self,request):
        id_tag = request.data.get('id_tag')
        connector_id = request.data.get('connector_id')
        user_token = request.data.get('user_token')
        token_check = appuser_info.objects.filter(token=user_token).first()
        if token_check:
            appuser_id = appuser_info.objects.get(token=user_token)
            charge_data = charge_info.objects.filter(Q(id_tag=id_tag) & Q(connector_id=connector_id)).values()
            order_number = charge_order.objects.filter(Q(appuser_id_fk=appuser_id) & Q(order_fee=None) & Q(order_status='unpaid')).values()
            if charge_data:
                return Response({'code': 200, 'data': {'charge_data':charge_data,'order_number':order_number}, 'message': 'Real-time data!'})
            else:
                return Response({'code': 201, 'data': {}, 'message': 'There is no charging information, please check the charging status!'})
        else:
            return Response({'code': 205, 'data': {}, 'message': 'token error or expired!'})

    def get(self,request):
        operator_token = request.headers.get("Token")
        operator_id = Token.objects.filter(key=operator_token).values('user_id')
        if operator_id:
            # station_id = charge_station_info.objects.filter(operators_id_fk=operator_id[0]['user_id']).values("station_id")
            pile_id = charge_pile.objects.filter(operators_id_fk=operator_id[0]['user_id']).values('pile_id')
            charge_information = charge_info.objects.filter(charge_pile_id__in = pile_id).values()
            return Response({"code":200,"data":charge_information,"message":"Charge information get successful"})
        return Response({"code":201,'data':{},"message":"Get operator id error!"})


    def delete(self,request):
        transaction_id = request.data.get('transaction_id')
        transaction_id_check = charge_info.objects.filter(transaction_id=transaction_id).first()
        if transaction_id_check:
            charge_info.objects.filter(transaction_id=transaction_id).delete()
            return Response({'code': 200, 'data': {},'message': 'delete successful!'})
        else:
            return Response({'code': 201, 'data': {},'message': 'transaction id no found!'})


# Management Platform charge pile management
class charge_pile_viewSet(viewsets.ModelViewSet):
    serializer_class = charge_pile_serializer
    pagination_class = PageNum
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend,filters.SearchFilter]
    filterset_fields = ['station_id_fk','pile_location_state']
    search_fields = ['pile_id','pile_charge_type','pile_location_state','pile_ratekw','pile_sn','station_id_fk__station_name']

    def get_queryset(self):
        queryset = charge_pile.objects.all()
        operator_token = self.request.headers.get('Token')
        operator_id = Token.objects.filter(key=operator_token).values('user_id')
        if operator_id:
            # station_id = charge_station_info.objects.filter(operators_id_fk=operator_id[0]['user_id']).values("station_id")
            queryset = queryset.filter(operators_id_fk=operator_id[0]['user_id'])
        return queryset


# Management platform order management
class charge_order_viewSet(viewsets.ModelViewSet):
    serializer_class = charge_order_serializer
    pagination_class = PageNum
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend,filters.SearchFilter]
    ordering_fields = ['order_id']
    filterset_fields = ['appuser_id_fk','pile_id_fk__pile_location_state']
    search_fields = ['order_id','appuser_id_fk__appuser_username','pile_id_fk__pile_charge_type','appuser_id_fk__appuser_username','order_end_datetime']

    def get_queryset(self):
        queryset = charge_order.objects.all().order_by('order_end_datetime')
        operator_token = self.request.headers.get('Token')
        operator_id = Token.objects.filter(key=operator_token).values('user_id')
        if operator_id:
            superuser = User.objects.filter(id=operator_id[0]['user_id']).values('is_superuser')
            if superuser[0]['is_superuser']:
                # station_id = charge_station_info.objects.filter(operators_id_fk=operator_id[0]['user_id']).values("station_id")
                queryset = queryset.order_by('order_end_datetime')
            else:
                pile_id = charge_pile.objects.filter(operators_id_fk=operator_id[0]['user_id']).values('pile_id')
                queryset = queryset.filter(pile_id_fk__in=pile_id).order_by('order_end_datetime')
        elif not operator_id:
            pile_id = [0]
            queryset = queryset.filter(pile_id_fk__in=pile_id).order_by('order_end_datetime')
        return queryset

# Management platform price management
class price_table_viewSet(viewsets.ModelViewSet):
    serializer_class = price_table_serializer
    pagination_class = PageNum
    filter_backends = [filters.SearchFilter]
    search_fields = ['price_id','station_id_fk__station_name']

    def get_queryset(self):
        queryset = price_table.objects.all()
        operator_token = self.request.headers.get('Token')
        operator_id = Token.objects.filter(key=operator_token).values('user_id')
        if operator_id:
            station_id = charge_station_info.objects.filter(operators_id_fk=operator_id[0]['user_id']).values("station_id")
            queryset = queryset.filter(station_id_fk__in=station_id)
        elif not operator_id:
            station_id = [0]
            queryset = queryset.filter(station_id_fk__in=station_id)
        return queryset



# Management platform vehicle management
class car_info_viewSet(viewsets.ModelViewSet):
    serializer_class = car_info_serializer
    pagination_class = PageNum
    filter_backends = [filters.SearchFilter]
    search_fields = ['car_id','car_registration_no','veh_id_fk__veh_brand','veh_id_fk__veh_model','veh_id_fk__charge_type']

    def get_queryset(self):
        queryset = car_info.objects.all()
        operator_token = self.request.headers.get('Token')
        operator_id = Token.objects.filter(key=operator_token).values('user_id')
        if operator_id:
            appuser_id = charge_order.objects.filter(operators_id_fk=operator_id[0]['user_id']).values("appuser_id_fk")
            queryset = queryset.filter(appuser_id_fk__in=appuser_id)
        elif not operator_id:
            appuser_id = [0]
            queryset = queryset.filter(appuser_id_fk__in=appuser_id)
        return queryset

# Management platform charge station management
class charge_station_info_viewSet(viewsets.ModelViewSet):
    queryset = charge_station_info.objects.all()
    serializer_class = charge_station_info_serializer
    pagination_class = PageNum
    filter_backends = [filters.SearchFilter]
    search_fields = ['station_location_state','station_name']

    def get_queryset(self):
        queryset = charge_station_info.objects.all()
        operator_token = self.request.headers.get('Token')
        operator_id = Token.objects.filter(key=operator_token).values('user_id')
        if operator_id:
            queryset = queryset.filter(operators_id_fk__in=operator_id)
        elif not operator_id:
            operator_id = [0]
            queryset = queryset.filter(operators_id_fk__in=operator_id)
        return queryset

# Management platform app user management
class appuser_info_viewSet(viewsets.ModelViewSet):
    serializer_class = appuser_info_serializer
    pagination_class = PageNum
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend,filters.SearchFilter]
    filterset_fields = ['token','appuser_username','appuser_id']
    search_fields = ['token','appuser_username','appuser_id','appuser_lastname','appuser_postcode']

    def get_queryset(self):
        queryset = appuser_info.objects.all()
        operator_token = self.request.headers.get('Token')
        operator_id = Token.objects.filter(key=operator_token).values("user_id")
        if operator_id:
            operator_info = User.objects.filter(id=operator_id[0]["user_id"]).values('is_superuser')
            if operator_info[0]['is_superuser'] == True:
                return queryset
            else:
                appuser_id = [0]
                queryset = queryset.filter(appuser_id__in=appuser_id)
        return queryset


# Management platform statement management
class statement_info_viewSet(viewsets.ModelViewSet):
    serializer_class = statement_info_serializer
    pagination_class = PageNum
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend,filters.SearchFilter]
    filterset_fields = ['statement_datetime']
    search_fields = ['operators_id_fk__username','statement_id']

    def get_queryset(self):
        queryset = statement_info.objects.all()
        operator_token = self.request.headers.get('Token')
        operator_id = Token.objects.filter(key=operator_token).values('user_id')
        if operator_id:
            queryset = queryset.filter(operators_id_fk__in=operator_id)
        elif not operator_id:
            operator_id = [0]
            queryset = queryset.filter(operators_id_fk__in=operator_id)
        return queryset


# Management platform operator management
class OperatorsInfoView(viewsets.ModelViewSet):
    serializer_class = operators_info_serializer
    pagination_class = PageNum
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend,filters.SearchFilter]
    search_fields = ['user_id_fk__username','user_id_fk','operators_code','operators_state']

    def get_queryset(self):
        queryset = operators_info.objects.all()
        operator_token = self.request.headers.get('Token')
        operator_id = Token.objects.filter(key=operator_token).values('user_id')
        if operator_id:
            operator_info = User.objects.filter(id=operator_id[0]["user_id"]).values('is_superuser')
            if operator_info[0]['is_superuser'] == True:
                return queryset
            else:
                queryset = queryset.filter(user_id_fk__in=operator_id)
        elif not operator_id:
            operator_id = [0]
            queryset = queryset.filter(user_id_fk__in=operator_id)
        return queryset

# Management platform price type management （foreign key table）
class price_type_info_viewSet(viewsets.ModelViewSet):
    queryset = price_type_info.objects.all()
    serializer_class = price_type_info_serializer
    pagination_class = PageNum

# Management platform vehicle brand management （foreign key table）
class vehicle_viewSet(viewsets.ModelViewSet):
    queryset = vehicle.objects.all()
    serializer_class = vehicle_serializer
    pagination_class = PageNum


# OCPP
class StartOCPPView(APIView):
    def post(self, request):
        id_tag = request.data.get('id_tag')
        connector_id = request.data.get('connector_id')
        user_token = request.data.get('user_token')
        order_start_time = request.data.get('order_start_time')
        id_tag_list = charge_pile.objects.values_list('pile_sn', flat=True)
        appuser_id = appuser_info.objects.filter(token=user_token).values()[0]['appuser_id']
        data = {'connector_id':int(connector_id),"id_tag":id_tag,'appuser_id':appuser_id}
        token = appuser_info.objects.filter(token=user_token).first()
        if token:
            if id_tag in list(id_tag_list):
                pile_id_fk = charge_pile.objects.get(Q(pile_sn=id_tag)&Q(pile_connect_no=connector_id))
                appuser_id_fk = appuser_info.objects.get(token=user_token)
                requests.post('http://tpterp.com:8082/remote_start', data=json.dumps(data))
                charge_info.objects.filter(Q(id_tag=id_tag) & Q(connector_id=connector_id)).update(appuser_id_fk=appuser_id)
                order_number = random.randint(100000000, 999999999)
                order_check = charge_order.objects.filter(order_status='unpaid').first()
                if not order_check:
                    charge_order.objects.create(
                        order_start_datetime=order_start_time,
                        pile_id_fk=pile_id_fk,
                        appuser_id_fk=appuser_id_fk,
                        order_number = order_number
                                                )
                    charge_info.objects.filter(Q(id_tag=id_tag) & Q(connector_id=connector_id)).update(
                        appuser_id_fk=appuser_id)
                    return Response({'code': 200, 'data': {'order_number':order_number}, 'message': 'Charge Pile Started!'})
                else:
                    order_check = charge_order.objects.filter(order_status='unpaid').values()
                    order_unpaid_number = order_check[0]['order_number']
                    return Response({'code': 200, 'data': {'order_number': order_unpaid_number}, 'message': 'Unpaid order already exists!'})
            else:
                return Response({'code': 201, 'data': {}, 'message': 'ID tag or Connect ID Error!'})
        else:
            return Response({'code': 205, 'data': {}, 'message': 'token error or expired!'})

    # def ChargingStatus(appuser_id):



class StopOCPPView(APIView):
    def post(self, request):
        id_tag = request.data.get('id_tag')
        connector_id = request.data.get('connector_id')
        user_token = request.data.get('user_token')
        order_stop_time = request.data.get('order_stop_time')
        charge_rate = charge_pile.objects.filter(Q(pile_sn=id_tag) & Q(pile_connect_no=connector_id)).values()[0]['charge_price']
        id_tag_list = charge_pile.objects.values_list('pile_sn', flat=True)
        token_check = appuser_info.objects.filter(token=user_token).first()
        if token_check:
            appuser_id = appuser_info.objects.get(token=user_token)
            charging_check = charge_info.objects.filter(
                Q(id_tag=id_tag) & Q(connector_id=connector_id)).first()
            if id_tag in list(id_tag_list) and charging_check:
                last_record = charge_info.objects.filter(Q(id_tag=id_tag) & Q(connector_id=connector_id)& Q(appuser_id_fk=appuser_id)).values()
                transaction_id = last_record[0]['transaction_id']
                order_info = last_record[0]['meter_value']
                data = {'transaction_id': transaction_id, "id_tag": id_tag}
                requests.post('http://tpterp.com:8082/remote_stop', data=json.dumps(data))
                # charge_info.objects.filter(
                #     Q(id_tag=id_tag) & Q(connector_id=connector_id) & Q(appuser_id_fk=appuser_id)).delete()。
                if eval(order_info)[0]['sampled_value'][2]['value'] != 0:
                    charge_order.objects.filter(Q(appuser_id_fk=appuser_id) & Q(order_status='unpaid')).update(
                        order_end_datetime=order_stop_time,
                        order_fee=charge_rate*Decimal(eval(order_info)[0]['sampled_value'][2]['value'])/1000,
                        charge_capacity = eval(order_info)[0]['sampled_value'][2]['value']
                    )
                    return Response({'code': 200, 'data': {'lastest_info': order_info}, 'message': 'Charge Pile Stopped!'})
                else:
                    charge_order.objects.filter(Q(appuser_id_fk=appuser_id) & Q(order_status='paid')).update(
                        order_end_datetime=order_stop_time,
                        order_fee=charge_rate * Decimal(eval(order_info)[0]['sampled_value'][2]['value']) / 1000,
                        charge_capacity=eval(order_info)[0]['sampled_value'][2]['value']
                    )
                    return Response({'code': 200, 'data': {'lastest_info':order_info}, 'message': 'Charge Pile Stopped!'})
            else:
                return Response({'code': 201, 'data': {}, 'message': 'ID tag or Connect ID Error,please check the charging status!'})
        else:
            return Response({'code': 205, 'data': {}, 'message': 'token error or expired,please check the charging status!'})


# Management platform real time data showing
class DataInfoView(APIView):
    def post(self,request):
        station_id = request.GET.get('stationID')
        charge_pile_id_list = list(charge_pile.objects.filter(station_id_fk = station_id).values_list('pile_id',flat=True))
        if charge_pile_id_list:
            total_charge_pile = charge_pile.objects.filter(station_id_fk=station_id)
            unique_val = set()
            for obj in total_charge_pile:
                unique_val.add(obj.pile_sn)
            total_charge_pile_no = len(unique_val)
            total_charge_pile_av = charge_pile.objects.filter(Q(station_id_fk=station_id) & Q(pile_status='Available')).count()
            total_charge_pile_unav = charge_pile.objects.filter(Q(station_id_fk=station_id) & Q(pile_status='Unavailable')).count()
            total_charge_pile_charging = charge_pile.objects.filter(Q(station_id_fk=station_id) & Q(pile_status='Charging')).count()
            charge_info_list1 = charge_info.objects.filter(charge_pile_id__in=charge_pile_id_list).values('charge_pile_id','id_tag','transaction_id','meter_value')
            if charge_info_list1.exists():
                charge_realtime_info = []
                for li in list(charge_info_list1):
                    info_str = str(li['meter_value'])
                    info_list = eval(info_str.replace("'meter_value': ", "").replace('"',''))[0]['sampled_value']
                    pile_status = total_charge_pile.filter(pile_id=li['charge_pile_id']).values('pile_status')
                    info_dict = {'charge_pile_id': li['charge_pile_id'],'id_tag':li['id_tag'],'transaction_id':li['transaction_id'],'pile_status':pile_status[0]['pile_status']}
                    if info_list:
                        for obj in info_list:
                            info_dict[obj['measurand']] = obj['value']
                    else:
                        info_dict['Current.Import'] = '0'
                        info_dict['Voltage'] = '0'
                        info_dict['Energy.Active.Import.Register'] = '0'
                        info_dict['Power.Active.Import'] = '0'
                    charge_realtime_info.append(info_dict)
                if charge_realtime_info:
                    return Response({'code':200,'data':{'charge_pile_status_no':{'total_charge_pile':total_charge_pile_no,'total_avaliable_pile':total_charge_pile_av,'total_unavaliable_pile':total_charge_pile_unav,'total_charging_pile':total_charge_pile_charging},'all_data':charge_realtime_info},'message':'successful'})
                else:
                    return Response({'code':201,'data':{'charge_pile_status_no':{'total_charge_pile':total_charge_pile_no,'total_avaliable_pile':total_charge_pile_av,'total_unavaliable_pile':total_charge_pile_unav,'total_charging_pile':total_charge_pile_charging},'all_data':{}},'message':'nothing to be found!'})
            else:
                return Response({'code':201,'data':{'charge_pile_status_no':{'total_charge_pile':total_charge_pile_no,'total_avaliable_pile':total_charge_pile_av,'total_unavaliable_pile':total_charge_pile_unav,'total_charging_pile':total_charge_pile_charging},'all_data':{}},'message':'nothing to be found!'})
        else:
            return Response({'code':201,'data':{},'message':'nothing to be found!'})

    def get(self,request):
        operator_token = request.headers.get('Token')
        operator_id = Token.objects.filter(key=operator_token).values("user_id")
        if operator_id:
            station_id = charge_station_info.objects.filter(operators_id_fk=operator_id[0]['user_id']).values("station_id")
            if station_id:
                return Response({'code':'200','data':station_id,'message':'station id list request successful!'})
            else:
                return Response({'code':'201','data':station_id,'message':'No station under the operator'})
        return Response({'code': '201', 'data': {}, 'message': 'operator can not found!'})


# Management platform Australia states information
class AusStatesInfoView(APIView):
    def get(self,request):
        Aus_states = ['NSW','VIC','QLD','WA','SA','TAS','NT','ACT']
        return Response({'code':200,'data':Aus_states,'message':'Charge Pile Information!'})



# Management platform Web statement return url & create pdf
class statement_PDF_URL(APIView):
    def generate_pdf(self,operators_id,datetime):
        os.makedirs(os.path.dirname(f'web/statement/{operators_id}/statement_{datetime}.pdf'), exist_ok=True)
        pdf_file = canvas.Canvas(f'web/statement/{operators_id}/statement_{datetime}.pdf',pagesize=A4)
        logo_path = os.path.abspath("web/logo/t-power-logo.jpg")
        pdf_file.drawImage(logo_path,x=100,y=700,width=100,height=100)
        pdf_file.setFont("Helvetica", 12)
        pdf_file.drawString(100, 600, "Welcome to My Document")

        # save and close PDF file
        pdf_file.showPage()
        pdf_file.save()

    def get(self,request):
        operator_token = request.headers.get('Token')
        statement_date = request.GET.get('statement_date')
        #datetime = date.today()
        operator_id = Token.objects.filter(key=operator_token).values("user_id")
        if operator_id:
            operator_id = operator_id[0]['user_id']
            self.generate_pdf(operator_id,statement_date)
            pdf_file_url = f"http://tpterp.com/web/statement_download/?operators_id={operator_id}"
            return Response({'code':200,'pdf_download_url':pdf_file_url,'msg':'get url successful!'})
        return Response({'code':201,'data':{},'message':'error, can not find operator id!'})

# Management platform Web download pdf
class statement_generate_pdf(APIView):
    def get(self,request):
        operator_id = request.GET.get('operators_id')
        statement_date = request.GET.get('statement_date')
        #datetime = date.today()
        pdf_file = open(f'web/statement/{operator_id}/statement_{statement_date}.pdf',"rb")
        if pdf_file:
            response = FileResponse(pdf_file, as_attachment=True, filename=f'statement_{statement_date}.pdf')
            response["Content-Disposition"] = f'attachment; filename="statement_{statement_date}.pdf"'
            return response
        else:
            return Response({'code':201,'data':{},'message':'error, can not find file!'})


class TestStatement(APIView):

    def get_chargeorder_list(self,operator_token,month):
        operator_id = Token.objects.filter(key=operator_token).values("user_id")
        station_id_list = charge_station_info.objects.filter(operators_id_fk=operator_id[0]['user_id']).values('station_id')
        pile_list = charge_pile.objects.filter(station_id_fk__in=station_id_list).values('pile_id')
        charge_order_list = charge_order.objects.filter(pile_id_fk__in=pile_list, order_end_datetime__month= month).values('pile_id_fk','order_start_datetime','order_end_datetime','charge_capacity','order_fee').order_by('order_start_datetime')
        return charge_order_list

    # def create_header(self, canvas, doc):
    #     # Customize your header content here
    #     header_text = "My Custom Header"
    #
    #     canvas.saveState()
    #     canvas.setFont("Helvetica", 12)
    #     canvas.drawString(doc.leftMargin, doc.height + doc.topMargin + 10, header_text)
    #     canvas.restoreState()
    #
    # def create_footer(self, canvas, doc):
    #     # Customize your footer content here
    #     footer_text = "Page {}/{}".format(canvas.getPageNumber(), doc.page)
    #
    #     canvas.saveState()
    #     canvas.setFont("Helvetica", 10)
    #     canvas.drawString(doc.leftMargin, doc.bottomMargin - 10, footer_text)
    #     canvas.restoreState()

    def get(self,request):
        operator_token = '8a84a7b75dae3093f71e1c8b74f1582c8a6dad91'
        month = 6
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'
        pdf_palt = canvas.Canvas(response,pagesize=A4)
        pdf_palt.setFont('Times-Roman',14)
        charge_order_list = self.get_chargeorder_list(operator_token,month)
        charge_order_list_new = []
        order_data = [['Pile Id','Order Start Time', 'Order End Time', 'Charge Capacity (kWh)', 'Order Fee (AU$)']]
        for order in charge_order_list:
            if order['pile_id_fk'] not in charge_order_list_new:
                list_order = [order['pile_id_fk'],order['order_start_datetime'].strftime('%Y-%m-%d %H:%M:%S'),order['order_end_datetime'].strftime('%Y-%m-%d %H:%M:%S'),order['charge_capacity'],order['order_fee']]
                order_data.append(list_order)
                charge_order_list_new.append(order['pile_id_fk'])
            else:
                list_order = ['',order['order_start_datetime'].strftime('%Y-%m-%d %H:%M:%S'),order['order_end_datetime'].strftime('%Y-%m-%d %H:%M:%S'),order['charge_capacity'],order['order_fee']]
                order_data.append(list_order)
        graphfile = Graphs()
        graphfile.draw_img("web/logo/t-power-logo.jpg", pdf_palt)
        customer_detail = ['Customer Detail','Company Name','Address','Email','Phone']
        space = ['','','','','']
        company_detail = ['Statement Detail','Statement No.','Address','Email','Phone']
        graphfile.draw_column_table(customer_detail,space,company_detail,pdf_palt)
        pdf_palt.drawCentredString(A4[0]/2,610,'T-power Operator Monthly Statement')
        # graphfile.draw_little_title('T-power Operator Monthly Statement')
        graphfile.draw_table(order_data,pdf_palt)
        pdf_palt.drawCentredString(A4[0]/2,610,'Pie Charts')

        pdf_palt.save()
        return response




    # def get(self,request):
    #     # operator_token = request.headers.get('Token')
    #     global list
    #     operator_token = '8a84a7b75dae3093f71e1c8b74f1582c8a6dad91'
    #     # month = date.today().month
    #     month = 6
    #     charge_order_list = self.get_chargeorder_list(operator_token,month)
    #     charge_order_list_new = []
    #     order_data = [['Pile Id','Order Start Time', 'Order End Time', 'Charge Capacity (kWh)', 'Order Fee (AU$)']]
    #     for order in charge_order_list:
    #         if order['pile_id_fk'] not in charge_order_list_new:
    #             list_order = [order['pile_id_fk'],order['order_start_datetime'].strftime('%Y-%m-%d %H:%M:%S'),order['order_end_datetime'].strftime('%Y-%m-%d %H:%M:%S'),order['charge_capacity'],order['order_fee']]
    #             order_data.append(list_order)
    #             charge_order_list_new.append(order['pile_id_fk'])
    #         else:
    #             list_order = ['',order['order_start_datetime'].strftime('%Y-%m-%d %H:%M:%S'),order['order_end_datetime'].strftime('%Y-%m-%d %H:%M:%S'),order['charge_capacity'],order['order_fee']]
    #             order_data.append(list_order)
    #
    #     doc = SimpleDocTemplate('report.pdf',pagesize=A4)
    #     graphfile = Graphs()
    #     graphic_content = list()
    #     graphic_content.append(graphfile.draw_img("web/logo/t-power-logo.jpg",doc))
    #     graphic_content.append(Spacer(1, 0.8 * inch))
    #     customer_detail = ['Customer Detail','Company Name','Address','Email','Phone']
    #     space = ['','','','','']
    #     company_detail = ['Statement Detail','Statement No.','Address','Email','Phone']
    #     graphic_content.append(graphfile.draw_column_table(customer_detail,space,company_detail,doc))
    #     graphic_content.append(Spacer(1, 0.5 * inch))
    #     graphic_content.append(graphfile.draw_little_title('T-power Operator Monthly Statement'))
    #     graphic_content.append(Spacer(1, 0.2 * inch))
    #     graphic_content.append(graphfile.draw_table(order_data,doc))
    #     doc.build(graphic_content)
    #
    #
    #     with open('report.pdf','rb') as f:
    #         pdf_data = f.read()
    #     response = HttpResponse(content_type='application/pdf')
    #     response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    #     response.write(pdf_data)
    #     return response



class TestView(APIView):
    def post(self,request):
        user_token = request.data.get('user_token')
        user_id_fk = appuser_info.objects.get(token=user_token)
        test = charge_order.objects.filter(appuser_id_fk=user_id_fk).values()
        return Response({'code': 200, 'data': test, 'message': 'Successful!'})

