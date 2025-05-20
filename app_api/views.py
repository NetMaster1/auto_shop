from django.shortcuts import render, redirect
from rest_framework import viewsets
from .models import ServerResponse
from app_product.models import Product, RemainderHistory, DocumentType
from .serializers import ServerResponseSerializer
import json
import requests
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
import datetime
import pytz

# Create your views here.


class ServerResponseView(viewsets.ModelViewSet):
  
    queryset=ServerResponse.objects.all()
    serializer_class=ServerResponseSerializer


@csrf_exempt #отключает защиту csrf
def ozon_push(request):
    if request.method == 'POST':
      try:
        #получение данных запроса POST от стороннего сайта в формате json
        data = json.loads(request.body)
        print(data)
        data=json.dumps(data)
        print(data)
        message_type=data.get("message_type")
        if message_type=='TYPE_PING':
          #print(message_type)
          # time = data.get("time")
          # print (time)
          #adding seconds & microseconds to 'dateTime' since it comes as '2021-07-10 01:05:03:00' and we need it real value of seconds & microseconds
          # current_dt=datetime.datetime.now()
          # mics=current_dt.microsecond
          # tdelta_1=datetime.timedelta(microseconds=mics)
          # secs=current_dt.second
          # tdelta_2=datetime.timedelta(seconds=secs)
          # tdelta_3=tdelta_1+tdelta_2
          # dateTime=dateTime+tdelta_2

          tdelta=datetime.timedelta(hours=3)
          dT_utcnow=datetime.datetime.now(tz=pytz.UTC)#Greenwich time aware of timezones
          dateTime=dT_utcnow+tdelta
          #converts django time to string
          dateTime=datetime.datetime.strftime(dateTime, "%Y-%m-%dT%H:%M:%SZ")
          #dispays milliseconds in string format
          # datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-2]

          json_data = {
            "version": "3.13.1",
            "name": "python",
            "time": dateTime
          }
          print(json_data)
        elif message_type=="TYPE_NEW_POSTING":
          status='initiated by ozon'
          print(message_type)
          time = data.get("in_process_at")
          shipment_id=data.get('posting_number')
          #print(time)
          #print('=================')
          # converting dateTime in str format (2021-07-08T01:05) to django format ()
          # dateTime = datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M")
          # print(dateTime)
          # #adding seconds & microseconds to 'dateTime' since it comes as '2021-07-10 01:05:03:00' and we need it real value of seconds & microseconds
          # current_dt=datetime.datetime.now()
          # mics=current_dt.microsecond
          # tdelta_1=datetime.timedelta(microseconds=mics)
          # secs=current_dt.second
          # tdelta_2=datetime.timedelta(seconds=secs)
          # tdelta_3=tdelta_1+tdelta_2
          # dateTime=dateTime+tdelta_3
          # print(dateTime)
          # else:
          tdelta=datetime.timedelta(hours=3)
          dateTime=datetime.datetime.now()
          dT_utcnow=datetime.datetime.now(tz=pytz.UTC)#Greenwich time aware of timezones
          dateTime=dT_utcnow+tdelta
          print(dateTime)
        
      
          doc_type = DocumentType.objects.get(name="Продажа ТМЦ")
          product_sold=data.get('products')
          print(product_sold)
          product=product_sold[0]
          #print(product)
          sku=product['sku']
          #print(f"SKU: {sku}")
          quantity=product['quantity']
          #print(f"Quantity: {quantity}")

          item=Product.objects.get(ozon_id=sku)
          if RemainderHistory.objects.filter(ozon_id=sku, created__lt=dateTime).exists():
            rho_latest_before = RemainderHistory.objects.filter(ozon_id=sku,  created__lt=dateTime).latest('created')
            pre_remainder=rho_latest_before.current_remainder
          else:
            pre_remainder=0
          print(pre_remainder)
          rho = RemainderHistory.objects.create(
            rho_type=doc_type,
            created=dateTime,
            article=item.article,
            ozon_id=sku,
            name=item.name,
            status=status,
            shipment_id=shipment_id,
            pre_remainder=pre_remainder,
            incoming_quantity=0,
            outgoing_quantity=int(quantity),
            current_remainder=pre_remainder - int(quantity),
            #retail_price=int(retail_price),
            # total_retail_sum=int(row.Retail_Price) * int(row.Qnty),
            )
          json_data = {
            "result": True
            }
        else:
          json_data = {
              "error": {
                "code": "ERROR_UNKNOWN",
                "message": "message_type is not defined",
                "details": None
              }
        }
      except:
        json_data = {
            "error": {
              "code": "ERROR_UNKNOWN",
              "message": "ошибка",
              "details": None
            }
        }
      
      #Sending the answer in json format via HttpResponse method
      #converts python dictionnary to json object
      # json_data=json.dumps(json_data)
      # print(json_data)
      # return HttpResponse(json_data, content_type='application/json')

      #Sending the answer in json format via JsonRespose method.
      #It's a djago method which converts python dict to json & automatically sets the required headers.
      print('========================')
      print('my server response')
      print('json_data')
      return JsonResponse(json_data, safe=False)
      #return JsonResponse(json_data, status=200)

      #messages.success(request, data)   
      #return redirect("dashboard")
