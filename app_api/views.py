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
import pandas
import time

# Create your views here.


class ServerResponseView(viewsets.ModelViewSet):
  
    queryset=ServerResponse.objects.all()
    serializer_class=ServerResponseSerializer

#url, куда приходит post request from ozon ( push уведомление) в формате json on поступившем заказе 
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

          #editing current quatityt in product table for future reports
          #taking current qunatity report based on rho table takes too much time
          product.quantity=rho.current_remainder
          product.total_sum=rho.current_remainder * product.av_price
          product.save()

          #changing qnty at WB
          if product.wb_bar_code:
            if product.length < 120:
              warehouseId=1368124
            else:
              warehouseId=1512363
            url=f'https://marketplace-api.wildberries.ru/api/v3/stocks/{warehouseId}'
            headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}
            stock_arr=[]
            wb_bar_code=str(product.wb_bar_code)
            qnty=rho.current_remainder
            stock_dict={
                "sku": wb_bar_code,#WB Barcode
                "amount": qnty,
            }
            stock_arr.append(stock_dict)
            params= {
                "stocks": stock_arr  
            }
            response = requests.put(url, json=params, headers=headers)
            #status_code=response.status_code
            #Status Code: 204 No Content
            #There is no content to send for this request except for headers.


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
      #before using HTTPResponse method you have to manually convert python dictionnary to json object which is done in the 
      #following string
      # json_data=json.dumps(json_data)
      # print(json_data)
      # return HttpResponse(json_data, content_type='application/json')

      #Sending the answer in json format via JsonRespose method.
      #It's a djago method which converts python dict to json & automatically & sets the required headers.
      #headers display which format the data is formatted in (json, dict or others)
      # a= JsonResponse(json_data, safe=False)
      # print(a)
      return JsonResponse(json_data, safe=False)

      #return JsonResponse(json_data, status=200)

      #messages.success(request, data)   
      #return redirect("dashboard")
#===================================WB Reference Data===========================================
def wb_test(request):
  #url = "https://common-api.wildberries.ru/ping"
  url = "https://common-api.wildberries.ru/api/v1/seller-info"
  headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}  
  response = requests.get(url, headers=headers)
  status_code=response.status_code
  a=response.json()
  print(f'status_code: {status_code}')
  print(a)

  messages.error(request,f'WB Response: {a}')
  return redirect ('dashboard')

def wb_categories (request):
  url="https://content-api.wildberries.ru/content/v2/object/parent/all"
  headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}  
  response = requests.get(url, headers=headers)
  status_code=response.status_code
  a=response.json()
  print(f'status_code: {status_code}')
  #print(a)
  b=a['data']
  for i in b:
    print(i)
  
  messages.error(request,f'WB Response: {a}')
  return redirect ('dashboard')

def wb_subjects (request):
  url="https://content-api.wildberries.ru/content/v2/object/all"
  headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}  
  params = {'parentID': '8891', 'limit': 1000}

  response = requests.get(url, headers=headers,  params=params,)
  status_code=response.status_code
  a=response.json()
  print(f'status_code: {status_code}')
  #print(a)
  b=a['data']
  for i in b:
    print(i)
  
  messages.error(request,f'WB Response: {a}')
  return redirect ('dashboard')

def wb_colors (request):
  url="https://content-api.wildberries.ru/content/v2/directory/colors"
  headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}  
  response = requests.get(url, headers=headers)
  status_code=response.status_code
  a=response.json()
  print(f'status_code: {status_code}')
  #print(a)
  b=a['data']
  for i in b:
    print(i)
  
    messages.error(request,f'WB Response: {i}')
  return redirect ('dashboard')

def wb_country_of_manufacture(request):
  url="https://content-api.wildberries.ru/content/v2/directory/countries"
  headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}  
  response = requests.get(url, headers=headers)
  status_code=response.status_code
  a=response.json()
  print(f'status_code: {status_code}')
  #print(a)
  b=a['data']
  for i in b:
    print(i)
  
    messages.error(request,f'WB Response: {i}')
  return redirect ('dashboard')

def wb_subject_specs (request):
  subjectID=2251
  url=f'https://content-api.wildberries.ru/content/v2/object/charcs/{subjectID}'
  headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}  

  response = requests.get(url, headers=headers)
  status_code=response.status_code
  a=response.json()
  print(f'status_code: {status_code}')
  #print(a)
  b=a['data']
  for i in b:
    print(i)
  
  messages.error(request,f'WB Response: {a}')
  return redirect ('dashboard')

def wb_limits (request):
  url=f'https://content-api.wildberries.ru/content/v2/cards/limits'
  headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}  

  response = requests.get(url, headers=headers)
  status_code=response.status_code
  a=response.json()
  print(f'status_code: {status_code}')
  print(a)
  # b=a['data']
  # for i in b:
  #   print(i)
  
  messages.error(request,f'WB Response: {a}')
  return redirect ('dashboard')

def wb_change_qnty (request):
  warehouseId=1368124
  url=f'https://marketplace-api.wildberries.ru/api/v3/stocks/{warehouseId}'
  headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}

  params= {
    "stocks": [
      {
        "sku": "447261570",# WB_bar_code; Обязательно двойные кавычки
        "amount": 4
      }
    ]
  }
          
  response = requests.put(url, json=params, headers=headers)
  status_code=response.status_code
  a=response.json()
  print(f'status_code: {status_code}')
  print(a)
  messages.error(request,f'Status Code: {status_code}; WB Response: {a}')
  return redirect ('dashboard')

def wb_warehouse_list(request):
  url=f'https://marketplace-api.wildberries.ru/api/v3/offices'
  headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}

  response = requests.get(url, headers=headers)
  status_code=response.status_code
  a=response.json()
  print(f'status_code: {status_code}')
  for i in a:
    print(i)
    messages.error(request,f'WB Response: {i}')
  return redirect ('dashboard')

def wb_create_warehouse(request):
  url=f'https://marketplace-api.wildberries.ru/api/v3/warehouses'
  headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}

  params = {
    'name': 'Склад Неклюдово',
    'officeId': 168
  }

  response = requests.post(url, json=params, headers=headers)
  status_code=response.status_code
  a=response.json()
  print(f'status_code: {status_code}')
  print(a)
  messages.error(request,f'WB Response: {a}')
  return redirect ('dashboard')

def wb_seller_warehouse_list(request):
  url=f'https://marketplace-api.wildberries.ru/api/v3/warehouses'
  headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}

  response = requests.get(url, headers=headers)
  status_code=response.status_code
  a=response.json()
  print(f'status_code: {status_code}')
  print(a)
  messages.error(request,f'WB Response: {a}')
  return redirect ('dashboard')

def wb_synchronize_orders_with_ozon_ver_1 (request):
    headers_ozon = {
        "Client-Id": "1711314",
        "Api-Key": 'b54f0a3f-2e1a-4366-807e-165387fb5ba7'
        }
    doc_type = DocumentType.objects.get(name="Продажа ТМЦ")
    status='initiated by wb'
    stock_arr=[]
	#Товары, цены и скидки для них. Максимум 1 000 товаров. Цена и скидка не могут быть пустыми одновременно.
	#Максимум 10 запросов за 6 секунд для всех методов категории Цены и скидки на один аккаунт продавца
    url=f'https://marketplace-api.wildberries.ru/api/v3/orders/new'
    headers_wb = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}
   
    response = requests.get(url, headers=headers_wb)
    print (response)
    status_code=response.status_code
    a=response.json()
    print(a)
    orders_list=a['orders']
    time.sleep(1)
    for i in orders_list:
        #print(f'Order #{n}: {i}')
        print('======================')
        order_id=i['id']
        print(i['id'])
        sku=i['skus']
        sku=sku[0]
        print(sku)
        
        if RemainderHistory.objects.filter(shipment_id=order_id).exists():
            print('Error_1. RHO with such shipment_id exists.')
            print("========================")
            continue

        else:
            tdelta=datetime.timedelta(hours=3)
            dateTime=datetime.datetime.now()
            dT_utcnow=datetime.datetime.now(tz=pytz.UTC)#Greenwich time aware of timezones
            dateTime=dT_utcnow+tdelta
            print(dateTime)
            print("========================")

            if Product.objects.filter(wb_bar_code=sku).exists():
                # print('ok')
                product=Product.objects.get(wb_bar_code=sku)
                article=product.article
            #     print(product.name)
            #     print(f'wb_bar_code: {product.wb_bar_code}')
            else:
                print('Error_2. No product with such wb_bar_code')
                continue
                
         
            if RemainderHistory.objects.filter(article=article, created__lt=dateTime).exists():
                # print("True")
                rho_latest_before = RemainderHistory.objects.filter(article=article,  created__lt=dateTime).latest('created')
                # print(rho_latest_before)
                # print(rho_latest_before.current_remainder)
                pre_remainder=rho_latest_before.current_remainder
            else:
                pre_remainder=0
                # print(pre_remainder)
            rho = RemainderHistory.objects.create(
                rho_type=doc_type,
                created=dateTime,
                article=product.article,
                wb_bar_code=sku,
                name=product.name,
                status=status,
                shipment_id=order_id,
                pre_remainder=pre_remainder,
                incoming_quantity=0,
                outgoing_quantity=1,
                current_remainder=pre_remainder - 1,
                #retail_price=int(retail_price),
                # total_retail_sum=int(row.Retail_Price) * int(row.Qnty),
                )
            product.quantity=rho.current_remainder
            product.total_sum=rho.current_remainder * product.av_price
            product.save()

    #         if product.ozon_id:
    #             stock_dict={
    #                 "offer_id": str(product.article),
    #                 "product_id": str(product.ozon_id),
    #                 "stock": rho.current_remainder,
    #                 #warehouse (Неклюдово)
    #                 "warehouse_id": 1020005000113280
    #                 }
    #             stock_arr.append(stock_dict)
                
    # if len(stock_arr) > 0:           
    #     for i in stock_arr:
    #         print (i)
    # else:
    #     print('stock_arr is empty')
        
    # task={
    #     "stocks" : stock_arr
    # }
    # response=requests.post('https://api-seller.ozon.ru/v2/products/stocks', json=task, headers=headers_ozon)

def yandex_category_list(request):
  url=f'https://api.partner.market.yandex.ru/v2/categories/tree'
  headers = {"Api-Key": "ACMA:lRqnoRHucSnmiG7kCDWEXVtYe99fBQN2obEHsYCR:21dc8ee9"}

  params ={
    "language": "RU"
  }

  response = requests.post(url, json=params, headers=headers)
  status_code=response.status_code
  print(status_code)
  a=response.json()
  print(f'status_code: {status_code}')
  print(a)