import json
import random
import requests
from _decimal import Decimal
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Q
from django.core.cache import cache
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.html import strip_tags
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, filters
import django_filters
from rest_framework.response import Response
from unicodedata import decimal

from charge_web.settings import EMAIL_HOST_USER
from web.models import card_info, charge_pile, charge_info, charge_order,charge_station_info, appuser_info,pile_schedule
from .serializers import charge_order_serializer,charge_info_serializer

from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
import datetime
import uuid
from twilio.rest import Client
import ast

account_sid = 'ACc1028bbc8e296c74ee480b064c9f5faf'
auth_token = '9ce67e1b193deb1ad64c44b7d024ebb0'
phone = '+61483927788'
local_tz = timezone.get_current_timezone()

class PageNum(PageNumberPagination):
    page_size = 10

# This is for Francis GIT test

# Twilio SMS Validation
class SendSMSView(APIView):
    def post(self, request):
        try:
            code = random.randint(100000, 999999)
            user_phone = request.data.get('userphone')
            client = Client(account_sid, auth_token)
            message = client.messages \
                .create(
                body=f'[T-power] Your verification code is {code} , expires in 5 minutes.',
                from_ = phone,
                to = user_phone
            )
            # Save the code to cache for later verification
            cache.set(user_phone, str(code), 300)
            return Response({'code':200,'data':{},'message': 'Verification code sent'}, status=200)
        except Exception as e:
            return Response({'code':201,'data':{},'message': 'Invalid phone number format'}, status=201)

# SMS Verify
class VerifySMSView(APIView):
    def post(self, request):
        user_phone = request.data.get('userphone')
        code = request.data.get('code')
        cached_code = cache.get(user_phone)
        if not cached_code or cached_code != code:
            return Response({'code':201,'data':{},'message': 'Invalid verification code'}, status=201)
        else:
            return Response({'code':200,'data':{},'message': 'verification code'}, status=200)

# APP user Register
class RegisterView(APIView):
    def post(self, request):
        user_first_name = request.data.get('userfirstname')
        user_last_name = request.data.get('userlastname')
        user_phone = request.data.get('userphone')
        user_email = request.data.get('useremail')
        pass_word = request.data.get('password')
        phone_list = appuser_info.objects.filter(Q(appuser_phone_no=user_phone[-9:]) | Q(appuser_email=user_email)).first()
        if phone_list:
            return Response({'code': 201, 'data': {}, 'message': 'Mobile phone number or email has been registered!'})
        elif len(pass_word) < 8:
            return Response({'code': 201, 'data': {}, 'message': 'The password must be greater than 8 characters!'})
        else:
            appuser_info.objects.create(
                appuser_firstname = user_first_name,
                appuser_lastname=user_last_name,
                appuser_phone_no = user_phone[-9:],
                appuser_password = pass_word,
                appuser_email = user_email,
                register_datetime = datetime.datetime.now()
            )
            subject = 'Registration Successful !'
            message = f'Dear {user_first_name},\n\nYour account has been successfully registered.' \
                      f' You can login with your Phone Number : {user_phone[3:]} or Email : {user_email}. Please do not reply to this email.\n\nT-power'
            from_email = EMAIL_HOST_USER
            to_email = [user_email]
            send_mail(subject, message, from_email, to_email, fail_silently=False)
            return Response({'code':200,'data':{},'message': 'Account create successfully.'})


# App user login
class apploginview(APIView):
    def post(self,request):
        appuser_account = request.data.get('user_account')
        apppassword = request.data.get('password')
        appuser_object = appuser_info.objects.filter(Q(appuser_phone_no = appuser_account[-9:]) | Q(appuser_email = appuser_account) , Q(appuser_password=apppassword)).first()
        print(appuser_account,apppassword,appuser_object)
        if not appuser_object:
            return Response({'code':201,'data':{},'message':'Invalid username or password!'})
        if appuser_object.token:
            appuser_info.objects.filter(
                Q(appuser_phone_no=appuser_account[-9:]) | Q(appuser_email=appuser_account)).update(token=None)
        token = str(uuid.uuid4())
        appuser_object.token = token
        appuser_object.save()
        user_id = appuser_info.objects.filter(Q(appuser_phone_no = appuser_account[-9:]) | Q(appuser_email = appuser_account),appuser_password=apppassword).values()[0]['appuser_id']
        user_card = card_info.objects.filter(appuser_id_fk=user_id).values()
        return Response({'code':200,'data':{'token':token,'user_account':appuser_account,'user_card':user_card},'message': 'Login successfully.'})

# App user logout
class applogoutview(APIView):
    def post(self,request):
        appuser_account = request.data.get('user_account')
        user_token = appuser_info.objects.filter(Q(appuser_phone_no = appuser_account[-9:]) | Q(appuser_email = appuser_account)).values('token')
        if user_token[0]['token'] is None:
            return Response({'code':201,'data':{},'message':'You have been successfully logged out.'})
        else:
            appuser_info.objects.filter(Q(appuser_phone_no = appuser_account[-9:]) | Q(appuser_email = appuser_account)).update(token=None)
            return Response({'code':200,'data':{},'message':'User logged out successfully.'})

# Login information return card information
class LoginInfoView(APIView):
    def post(self, request):
        user_token = request.data.get('user_token')
        token_list = appuser_info.objects.filter(token=user_token).values()
        if not token_list:
            return Response({'code': 205, 'data': {}, 'message': 'token error or expired!'})
        else:
            user_id = token_list[0]['appuser_id']
            user_card = card_info.objects.filter(appuser_id_fk=user_id).values()
            return Response({'code': 200, 'data': {'user_info':token_list,'user_card':user_card}, 'message': 'Got user information'})

# password update function
class PwdUpdateView(APIView):
    def post(self,request):
        user_phone = request.data.get('user_phone')
        code = request.data.get('code')
        #user_password_old = request.data.get('user_password_old')
        user_password_new = request.data.get('user_password_new')
        user_password_repeat = request.data.get('user_password_repeat')
        phone_check = appuser_info.objects.filter(appuser_phone_no=user_phone[-9:]).first()
        cached_code = cache.get(user_phone)
        if phone_check:
            user_info = appuser_info.objects.filter(appuser_phone_no=user_phone[-9:]).values()
            old_pass_world = user_info[0]['appuser_password']
            # if user_password_old != old_pass_world:
            #     return Response({'code': 201, 'data': {}, 'message': ' password error !'})
            if user_password_new != user_password_repeat:
                return Response({'code': 201, 'data': {}, 'message': 'You should enter the same password!'})
            elif not cached_code or cached_code != code:
                return Response({'code': 201, 'data': {}, 'message': 'Invalid verification code!'})
            else:
                appuser_info.objects.filter(appuser_phone_no=user_phone[-9:]).update(
                    appuser_password=user_password_repeat)
                return Response({'code': 200, 'data': {user_info}, 'message': 'update successfully!'})
        else:
            return Response({'code': 205, 'data': {}, 'message': 'The user token is wrong or expired!'})


# Credit Card information return
class CardInfoView(APIView):
    def post(self, request):
        card_number = request.data.get('card_number')
        card_vendor = request.data.get('card_vendor')
        card_CVC = request.data.get('card_CVC')
        card_first_name = request.data.get('card_first_name')
        card_last_name = request.data.get('card_last_name')
        card_expire_year = request.data.get('card_expire_year')
        card_expire_month = request.data.get('card_expire_month')
        user_card_token = request.data.get('user_card_token')
        user_token = request.data.get('user_token')
        token_check = appuser_info.objects.filter(token=user_token).first()
        if token_check:
            appuser_id = appuser_info.objects.get(token=user_token)
            # user_card = card_info.objects.filter(card_number=card_number).first()
            card_check = card_info.objects.filter(Q(card_number=card_number) & Q(appuser_id_fk=appuser_id)&Q(card_CVC=card_CVC)).first()
            if card_check or user_card_token == None:
                return Response({'code': 201, 'data': {}, 'message': 'The card already exists or The user card token can not be Null!'})
            else:
                card_info.objects.create(
                    create_date = timezone.make_aware(datetime.datetime.today(), local_tz),
                    card_number = card_number,
                    card_vendor = card_vendor,
                    card_CVC = card_CVC,
                    expire_date_year = card_expire_year,
                    expire_date_month = card_expire_month,
                    appuser_id_fk = appuser_id,
                    card_first_name = card_first_name,
                    card_last_name = card_last_name,
                    user_card_token = user_card_token
                )
                return Response({'code': 200, 'data': card_info.objects.filter(appuser_id_fk=appuser_id).values(), 'message': 'The card information has been saved successfully!'})
        return Response({'code': 205, 'data': {},'message': 'The user token is wrong or expired!'})

# Delete card information from 3rd part
class CardInfoDelView(APIView):
    def post(self, request):
        card_number = request.data.get('card_number')
        user_token = request.data.get('user_token')
        appuser_id = appuser_info.objects.get(token=user_token)
        # user_card = card_info.objects.filter(card_number=card_number).first()
        card_check = card_info.objects.filter(Q(card_number=card_number) & Q(appuser_id_fk=appuser_id)).first()
        if card_check:
            card_data = card_info.objects.filter(appuser_id_fk=appuser_id)
            card_data.delete()
            return Response({'code': 200, 'data': {}, 'message': 'The card has been deleted successfully!'})
        else:
            return Response({'code': 201, 'data': {}, 'message': 'The card does not exists!'})

# Update Card Information
class CardUpdateDelView(APIView):
    def post(self, request):
        card_number = request.data.get('card_number')
        card_vendor = request.data.get('card_vendor')
        card_CVC = request.data.get('card_CVC')
        card_first_name = request.data.get('card_first_name')
        card_last_name = request.data.get('card_last_name')
        card_expire_year = request.data.get('card_expire_year')
        card_expire_month = request.data.get('card_expire_month')
        user_card_token = request.data.get('user_card_token')
        user_token = request.data.get('user_token')
        token_check = appuser_info.objects.filter(token=user_token).first()
        print(card_number)
        if token_check:
            appuser_id = appuser_info.objects.get(token=user_token)
            card_info.objects.filter(appuser_id_fk=appuser_id).update(
                card_number = card_number,
                card_vendor = card_vendor,
                card_CVC=card_CVC,
                expire_date_year = card_expire_year,
                expire_date_month = card_expire_month,
                appuser_id_fk = appuser_id,
                card_first_name = card_first_name,
                card_last_name = card_last_name,
                user_card_token = user_card_token
            )
            return Response({'code': 200, 'data': {card_info.objects.filter(appuser_id_fk=appuser_id).values()}, 'message': 'The card has been updated!'})
        return Response({'code': 205, 'data': {}, 'message': 'The user token is wrong or expired!'})



# appuser get real time charge infomation
class ChargeInfoView(APIView):
    def post(self,request):
        id_tag = request.data.get('id_tag')
        connector_id = request.data.get('connector_id')
        user_token = request.data.get('user_token')
        token_check = appuser_info.objects.filter(token=user_token).first()
        if token_check:
            appuser_id = appuser_info.objects.get(token=user_token)
            charge_info.objects.filter(Q(id_tag=id_tag) & Q(connector_id=connector_id)).update(appuser_id_fk=appuser_id)
            charge_data = charge_info.objects.filter(Q(id_tag=id_tag) & Q(connector_id=connector_id)).values()
            order_number = charge_order.objects.filter(Q(appuser_id_fk=appuser_id) & Q(order_fee=None) & Q(order_status='unpaid')).values()
            # charge_data = charge_info.objects.filter(Q(id_tag=id_tag) & Q(connector_id=connector_id)).last()
            # charge_data_last = charge_info_serializer(charge_data).data
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
            station_id = charge_station_info.objects.filter(operators_id_fk=operator_id[0]['user_id']).values("station_id")
            pile_id = charge_pile.objects.filter(station_id_fk__in=station_id).values('pile_id')
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


class charge_order_viewSet(viewsets.ModelViewSet):
    serializer_class = charge_order_serializer
    pagination_class = PageNum
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend,filters.SearchFilter]
    filterset_fields = ['appuser_id_fk','pile_id_fk__pile_location_state']
    search_fields = ['order_id','pile_id_fk__pile_charge_type','appuser_id_fk__appuser_username','order_end_datetime']

    def get_queryset(self):
        #queryset = super().get_queryset()
        queryset = charge_order.objects.all()
        operator_token = self.request.headers.get('Token')
        #operator_token=self.request.data.get('operator_token')
        operator_id = Token.objects.filter(key=operator_token).values('user_id')
        if operator_id:
            station_id = charge_station_info.objects.filter(operators_id_fk=operator_id[0]['user_id']).values("station_id")
            pile_id = charge_pile.objects.filter(station_id_fk__in=station_id).values('pile_id')
            queryset = queryset.filter(pile_id_fk__in=pile_id)
        elif not operator_id:
            station_id = [0]
            pile_id = [0]
            queryset = queryset.filter(pile_id_fk__in=pile_id)
        return queryset


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


class DataInfoView(APIView):
    def post(self,request):
        station_id = request.GET.get('stationID')
        charge_pile_id_list = list(charge_pile.objects.filter(station_id_fk = station_id).values_list('pile_id',flat=True))
        if charge_pile_id_list:
            total_charge_pile = charge_pile.objects.filter(station_id_fk=station_id)
            #charge_pile_status_list = total_charge_pile.values('pile_id','pile_sn','pile_status')
            unique_val = set()
            for obj in total_charge_pile:
                unique_val.add(obj.pile_sn)
            total_charge_pile_no = len(unique_val)
            total_charge_pile_av = charge_pile.objects.filter(Q(station_id_fk=station_id) & Q(pile_status='available')).count()
            total_charge_pile_unav = charge_pile.objects.filter(Q(station_id_fk=station_id) & Q(pile_status='unavailable')).count()
            total_charge_pile_charging = charge_pile.objects.filter(Q(station_id_fk=station_id) & Q(pile_status='charging')).count()
            charge_info_list1 = charge_info.objects.filter(charge_pile_id__in=charge_pile_id_list).values('charge_pile_id','id_tag','transaction_id','meter_value')
            if charge_info_list1:
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
                    return Response({'code':201,'data':{},'message':'nothing to be found!'})
        else:
            return Response({'code':201,'data':{},'message':'nothing to be found!'})

    def get(self,request):
        operator_token = request.headers.get('operator_token')
        operator_id = Token.objects.filter(key=operator_token).values("user_id")
        if operator_id:
            station_id = charge_station_info.objects.filter(operators_id_fk=operator_id[0]['user_id']).values("station_id")
            if station_id:
                return Response({'code':'200','data':station_id,'message':'station id list request successful!'})
            else:
                return Response({'code':'201','data':station_id,'message':'No station under the operator'})
        return Response({'code': '201', 'data': {}, 'message': 'operator can not found!'})


# Australia states information
class AusStatesInfoView(APIView):
    def get(self,request):
        Aus_states = ['NSW','VIC','QLD','WA','SA','TAS','NT','ACT']
        return Response({'code':200,'data':Aus_states,'message':'Charge Pile Information!'})

class  PileScheduleView(APIView):
    def post(self,request):
        pile_sn = request.data.get('pile_sn')
        pile_check = charge_pile.objects.filter(pile_sn=pile_sn)
        if pile_check:
            pile_id = charge_pile.objects.get(pile_sn=pile_sn)
            available_time = pile_schedule.objects.filter(charge_pile_fk=pile_id).values()
            return Response({'code':200,'data':available_time,'message':'Charge Pile Schedule Information!'})
        else:
            return Response({'code':201,'data':{},'message':'Pile not found!'})


class GetOrderView(APIView):
    def post(self,request):
        user_token = request.data.get('user_token')
        token_check = appuser_info.objects.filter(token=user_token).first()
        if token_check:
            user_id_fk = appuser_info.objects.get(token=user_token)
            order_info = charge_order.objects.filter(appuser_id_fk=user_id_fk).values().order_by('-order_id')
            # order_info = charge_order.objects.filter(appuser_id_fk=user_id_fk).last()
            # test = charge_order_serializer(order_info).data
            return Response({'code':200,'data':{'tpye':1,'order_info':order_info},'message':'User orders Information!'})
        else:
            return Response({'code':205,'data':{},'message':'Token not found or expired!'})

class UserTypeView(APIView):
    def post(self,request):
        user_token = request.data.get('user_token')
        token_check = appuser_info.objects.filter(token=user_token).first()
        if token_check:
            user_id_fk = appuser_info.objects.get(token=user_token)
            charging_check = charge_info.objects.filter(appuser_id_fk=user_id_fk).first()
            order_check = charge_order.objects.filter(Q(appuser_id_fk=user_id_fk) & Q(order_status='unpaid')).first()
            if charging_check and order_check:
                user_type = 1
                charging_info = charge_info.objects.filter(appuser_id_fk=user_id_fk).values()
                return Response({'code': 200, 'data': {'user_type':user_type,'charging_info':charging_info}, 'message': 'User is charging!'})
            elif not charging_check and order_check:
                # order_check = charge_order.objects.filter(Q(appuser_id_fk=user_id_fk)&Q(order_status='unpaid')).first()
                unpaid_order = charge_order.objects.filter(Q(appuser_id_fk=user_id_fk)&Q(order_status='unpaid')).values()
                user_type = 2
                return Response({'code': 200, 'data': {'user_type': user_type,'unpaid_order':unpaid_order}, 'message': 'User has unpaid bills!'})
            else:
                user_type = 0
                return Response(
                    {'code': 200, 'data': {'user_type': user_type}, 'message': 'The user status is normal and can be charged!'})
        else:
            return Response({'code': 205, 'data': {}, 'message': 'Token not found or expired!'})

class SuccessfulPayView(APIView):
    def post(self,request):
        user_token = request.data.get('user_token')
        paid_code = request.data.get('paid_code')
        order_number = request.data.get('order_number')
        paid_token = request.data.get('paid_token')
        token_check = appuser_info.objects.filter(token=user_token).first()
        if token_check:
            user_id_fk = appuser_info.objects.get(token=user_token)
            charge_order.objects.filter(Q(appuser_id_fk=user_id_fk)&Q(order_number=order_number)).update(
                paid_code=paid_code,
                order_status='paid',
                paid_token=paid_token
            )
            order_info = charge_order.objects.filter(order_number=order_number).values()
            return Response({'code': 200, 'data': {'order_info':order_info}, 'message': 'The user status is normal and can be charged!'})
        else:
            return Response({'code': 205, 'data': {}, 'message': 'Token not found or expired!'})


class OCPPOnMeterView(APIView):
    def post(self,request):
        meter_value = request.data.get('meter_value')
        transaction_id = request.data.get('transaction_id')
        charge_info.objects.filter(transaction_id=transaction_id).update(
            meter_value = meter_value
        )
        return Response({'code': 200, 'data': {}, 'message': 'Successful!'})

class CreateChargingView(APIView):
    def post(self,request):
        transaction_id = request.data.get('transaction_id')
        connector_id = request.data.get('connector_id')
        id_tag = request.data.get('id_tag')
        charge_pile_id = charge_pile.objects.get(Q(pile_sn=id_tag)&Q(pile_connect_no=connector_id))
        charge_info.objects.create(
            start_time = timezone.make_aware(datetime.datetime.today(), local_tz),
            transaction_id = transaction_id,
            id_tag = id_tag,
            connector_id=connector_id,
            charge_pile_id = charge_pile_id
        )
        return Response({'code': 200, 'data': {}, 'message': 'Successful!'})


class ChargingCheckView(APIView):
    def get(self,request):
        charging_info = charge_info.objects.all().values()
        if charging_info:
            if charging_info[0]['meter_value'] != '':
                return Response({'code': 200, 'data': charging_info, 'message': 'Successful!'})
            else:
                return Response({'code': 201, 'data': charging_info, 'message': 'No meter value!'})
        else:
            return Response({'code': 201, 'data': {}, 'message': 'No info!'})

    def post(self,request):
        transaction_id = request.data.get('transaction_id')
        charging = charge_info.objects.filter(transaction_id=transaction_id).values()
        charging_modify = ast.literal_eval(charging[0]['meter_value'])
        charging_modify[0]['sampled_value'][0]['value'] = '0'
        charge_info.objects.filter(transaction_id=transaction_id).update(meter_value=charging_modify)
        return Response({'code': 200, 'data': {}, 'message': 'Successful!'})



# app using charge_pile API
class get_charge_pile(APIView):
    def get(self,request):
        total_charge_pile = charge_pile.objects.all().values()
        if total_charge_pile:
            return Response({"code":200,"results":total_charge_pile,"message":"get all data successful"})
        else:
            return Response({"code":201,"data":{},"message":"error, Can not find data!"})


class InvoiceView(APIView):
    def post(self,request):
        user_token = request.data.get('user_token')
        token_check = appuser_info.objects.filter(token=user_token).first()
        if token_check:
            user_id = appuser_info.objects.get(token=user_token)
            user_info = appuser_info.objects.filter(token=user_token).values()
            user_first_name = user_info[0]['appuser_firstname']
            user_email = user_info[0]['appuser_email']
            subject = 'T-Power Charge Invoice'

            order_data = charge_order.objects.filter(appuser_id_fk=user_id).values().last()
            invoice_number = order_data['order_number']
            capacity = order_data['charge_capacity']
            pile_number = charge_pile.objects.filter(pile_id=order_data['pile_id_fk_id']).values()[0]['pile_sn']
            unit_price = charge_pile.objects.filter(pile_id=order_data['pile_id_fk_id']).values()[0]['pile_ratekw']
            total = float(unit_price) * float(capacity)

            html_content = render_to_string(
                'invoice_template.html',
                {
                     'user_first_name': user_first_name,
                     'invoice_number':invoice_number,
                     'capacity':capacity,
                     'pile_number':pile_number,
                     'unit_price':unit_price,
                     'total': total,
                 })

            from_email = EMAIL_HOST_USER
            to_email = [user_email]
            email = EmailMultiAlternatives(subject,html_content,from_email, to_email)
            email.attach_alternative(html_content,'text/html')
            email.send()
        return Response({'code': 200, 'data': user_info, 'message': 'Successful!'})

class TestView(APIView):
    def post(self, request):
        user_token = request.data.get('user_token')
        user_info = appuser_info.objects.get(token=user_token)
        invoice_number = charge_order.objects.filter(appuser_id_fk=user_info).values().last()
        pile_number = charge_pile.objects.filter(pile_id=invoice_number['pile_id_fk_id']).values()[0]['pile_sn']
        print(pile_number)
        return Response({'code': 200, 'data': pile_number, 'message': 'Successful!'})

