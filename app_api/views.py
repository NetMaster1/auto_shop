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

def wb_create_product (request):
    url=f'https://content-api.wildberries.ru/content/v2/cards/upload'
    headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}  
    params = [
          {
            "subjectID": 2251,
            "variants": [
              {
                "vendorCode": "DK-IN-00081",
                "title": "Дефлектор капота NISSAN NOTE I (2005-2009) хэтчбек",
                "description": "Дефлектор капота это - стильный аксессуар",
                "brand": "Delta Avto",
                "dimensions": 
                  {
                    "length": 100,
                    "width": 30,
                    "height": 5,
                    "weightBrutto": 1
                  },
              

              "characteristics": [
                  {
                    "id": 5023,
                    "value": "Lada"
                  },
                  {
                    "id": 16532,
                    "name" : 'Granta'
                  },
                  {
                    "id": 17596,
                    "name" : 'пластик'
                  },
                  {
                    "id": 74242,
                    "name" : 'капот'
                  },
                  {
                    "id": 90702,
                    "name" : '1'
                  },
                  {
                    "id": 378533,
                    "name" : 'Дефлектор, крепеж, инструкция'
                  },
                  {
                    "id": 5522881,
                    "name" : 'DK-IN-00081'
                  },
                  {
                    "id": 14177451,
                    "name" : 'Россия'
                  },
                  {
                    "id": 14177451,
                    "name" : 'Россия'
                  },
              ],
              # "sizes": [
              #   {
              #   "techSize": "M",
              #   "wbSize": "42",
              #   "price": 2500,
              #   "skus": []
              #   }
              # ]
            }
          ]
        }
      ]

    response = requests.post(url, json=params, headers=headers)
    status_code=response.status_code
    a=response.json()
    print(f'status_code: {status_code}')
    print(a)
    # b=a['data']
    # for i in b:
    #   print(i)
    
    messages.error(request,f'WB Response: {a}')
    return redirect ('dashboard')

def wb_add_media_files (request):
  url=f'https://content-api.wildberries.ru/content/v3/media/save'
  headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}
  params = {
     "nmId": 447261570,
     "data": [
       "https://mp-system.ru/media/uploads/Nissan_Note_I_2005.png",
      #  "https://disk.yandex.ru/i/QAlZnFMAW11KQA",
      #  "https://disk.yandex.ru/i/vzbsu-k-Hmd5IA",
      #  "https://disk.yandex.ru/i/kmCMse7Ag4h__g."
     ]
  }
       
  response = requests.post(url, json=params, headers=headers)
  status_code=response.status_code
  a=response.json()
  print(f'status_code: {status_code}')
  print(a)
  messages.error(request,f'WB Response: {a}')
  return redirect ('dashboard')

def wb_change_qnty (request):
  url=f'https://content-api.wildberries.ru/content/v3/media/save'
  headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}
  params = {
     "nmId": 447261570,
     "data": [
       "https://mp-system.ru/media/uploads/Nissan_Note_I_2005.png",
      #  "https://disk.yandex.ru/i/QAlZnFMAW11KQA",
      #  "https://disk.yandex.ru/i/vzbsu-k-Hmd5IA",
      #  "https://disk.yandex.ru/i/kmCMse7Ag4h__g."
     ]
  }
           
  response = requests.post(url, json=params, headers=headers)
  status_code=response.status_code
  a=response.json()
  print(f'status_code: {status_code}')
  print(a)
  messages.error(request,f'WB Response: {a}')
  return redirect ('dashboard')

def wb_change_qnty (request):
  warehouseId=1368124
  url=f'https://marketplace-api.wildberries.ru/api/v3/stocks/{warehouseId}'
  headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}

  params= {
    "stocks": [
      {
        "sku": "447261570",#Артикул WB
        "amount": 5
      }
    ]
  }
          
  response = requests.put(url, json=params, headers=headers)
  status_code=response.status_code
  a=response.json()
  print(f'status_code: {status_code}')
  print(a)
  messages.error(request,f'WB Response: {a}')
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
