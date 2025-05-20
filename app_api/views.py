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
        #получение данных запроса POST от стороннего сайта в формате json и преобразование данных в формат словаря Python
        data = json.loads(request.body)
        print(data)

        #получение данных из текста в формате json
        #message_type=data.get("message_type")

        #далее уже работаем со словарём питон
        message_type=data['message_type']
        if message_type=='TYPE_PING':
          print(message_type)
        
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

        elif message_type=="TYPE_NEW_POSTING":
          status='initiated by ozon'
          shipment_id=data['posting_number']
          print(message_type)
          print(shipment_id)

          tdelta=datetime.timedelta(hours=3)
          dateTime=datetime.datetime.now()
          dT_utcnow=datetime.datetime.now(tz=pytz.UTC)#Greenwich time aware of timezones
          dateTime=dT_utcnow+tdelta
          print(dateTime)
        
          products=data['products']
          print(products)
          item=products[0]
          print(item)
          sku=item['sku']
          quantity=item['quantity']
          print(f'SKU: {sku}')
          print(f'Quantity: {quantity}')
          doc_type = DocumentType.objects.get(name="Продажа ТМЦ")
          print(doc_type)
        
          product=Product.objects.get(ozon_sku=sku)
          print(product.name)
          print(f'Ozon_id: {product.ozon_id}')
          print(f'Ozon_sku: {product.ozon_sku}')
          if RemainderHistory.objects.filter(ozon_id=product.ozon_id, created__lt=dateTime).exists():
            print("True")
            rho_latest_before = RemainderHistory.objects.filter(ozon_id=product.ozon_id,  created__lt=dateTime).latest('created')
            print(rho_latest_before)
            print(rho_latest_before.current_remainder)
            pre_remainder=rho_latest_before.current_remainder
          else:
            pre_remainder=0
            print(pre_remainder)
          rho = RemainderHistory.objects.create(
            rho_type=doc_type,
            created=dateTime,
            article=product.article,
            ozon_id=product.ozon_id,
            ozon_sku=sku,
            name=product.name,
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

      # a= JsonResponse(json_data, safe=False)
      # print(a)
      return JsonResponse(json_data, safe=False)

      #return JsonResponse(json_data, status=200)

      #messages.success(request, data)   
      #return redirect("dashboard")
