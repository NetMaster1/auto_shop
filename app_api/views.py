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

# Create your views here.


class ServerResponseView(viewsets.ModelViewSet):
  
    queryset=ServerResponse.objects.all()
    serializer_class=ServerResponseSerializer


@csrf_exempt #отключает защиту csrf
def ozon_push(request):
    if request.method == 'POST':
      try:
        #получение данных запроса POST в формате json
        data = json.loads(request.body)
        print(data)
        message_type=data.get("message_type")
        if message_type=='string':
          time = data.get("time")
          print (time)
          json_data = {
            "version": "3.13.1",
            "name": "python",
            "time": time
          }
        elif message_type=="TYPE_NEW_POSTING":
          time = data.get("in_process_at")
          # converting dateTime in str format (2021-07-08T01:05) to django format ()
          dateTime = datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M")
          #adding seconds & microseconds to 'dateTime' since it comes as '2021-07-10 01:05:03:00' and we need it real value of seconds & microseconds
          current_dt=datetime.datetime.now()
          mics=current_dt.microsecond
          tdelta_1=datetime.timedelta(microseconds=mics)
          secs=current_dt.second
          tdelta_2=datetime.timedelta(seconds=secs)
          tdelta_3=tdelta_1+tdelta_2
          dateTime=dateTime+tdelta_3
          # else:
          #     tdelta=datetime.timedelta(hours=3)
          #     dT_utcnow=datetime.datetime.now(tz=pytz.UTC)#Greenwich time aware of timezones
          #     dateTime=dT_utcnow+tdelta


          doc_type = DocumentType.objects.get(name="Продажа ТМЦ")
          product_sold=data.get('products')
          product=product_sold[0]
          sku=product['sku']
          quantity=product['quantity']

          item=Product.objects.get(ozon_id=sku)
          if RemainderHistory.objects.filter(ozon_id=sku, created__lt=dateTime).exists():
            rho_latest_before = RemainderHistory.objects.filter(ozon_id=sku,  created__lt=dateTime).latest('created')
            pre_remainder=rho_latest_before.current_remainder
          else:
            pre_remainder=0
          rho = RemainderHistory.objects.create(
            rho_type=doc_type,
            created=dateTime,
            article=item.article,
            ozon_id=sku,
            name=product.name,
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
        return JsonResponse(json_data, safe=False)
      
      except:
        json_data = {
            "error": {
              "code": "ERROR_UNKNOWN",
              "message": "ошибка",
              "details": None
            }
        }
    messages.success(request, data)   
    return redirect("dashboard")
