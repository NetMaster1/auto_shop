from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from rest_framework import viewsets
from .models import ServerResponse
from app_product.models import Product, RemainderHistory, DocumentType
from app_purchase.models import Order, OrderItem, Cart, CartItem
from app_reference.models import SDEK_Office
from .serializers import ServerResponseSerializer
import json
import requests
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
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
def ozon_push(request):#receives a notification from ozon on a new order
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

          if RemainderHistory.objects.filter(article=product.article, created__lt=dateTime).exists():
            print("True")
            rho_latest_before = RemainderHistory.objects.filter(article=product.article,  created__lt=dateTime).latest('created')
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

#url, куда приходит уведомление от ю-касса. Используется для изменения статуса заказа на "succeeded"
#и формирования заказа на отпрвку в СДЕК
@csrf_exempt #отключает защиту csrf
def payment_status(request):#receives an http notice from Y-kassa on a successful payment
	if request.method=='POST':
		doc_type = DocumentType.objects.get(name="Продажа ТМЦ")
		tdelta=datetime.timedelta(hours=3)
		dT_utcnow=datetime.datetime.now(tz=pytz.UTC)#Greenwich time aware of timezones
		dateTime=dT_utcnow+tdelta
		#converts django time to string
		dateTime=datetime.datetime.strftime(dateTime, "%Y-%m-%dT%H:%M:%SZ")
		#dispays milliseconds in string format
		# datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-2]
		import json
		try:
			data = json.loads(request.body)
			#data = json.loads(request.body.decode('utf-8'))
			object=data.get('object')
			order_id=object.get('description')
			status=object.get('status')
			order=Order.objects.get(id=order_id)
			if order.corresponding_rhos_created == True and order.status=='succeeded':
				print ('rho has been previously created')
			else:
				print('response from Y-kassa: ')
				print(data)
				order.status=status
				order.save()
				if order.status=='succeeded':
					order.corresponding_rhos_created=True
					order.save()
					print('========================')
					print('order payment succeeded')
                    #==============================Getting SDEK Delivery Point====================
					delivery_point=SDEK_Office.objects.get(address_full=order.delivery_point)
					print('========================')
					print(f'Код пункта выдачи СДЕК: {delivery_point.code}')
					print('========================')
					contragent_full_name=[order.receiver_firstName, order.receiver_lastName]
					contragent_full_name = ' '.join(contragent_full_name)
					#================End fo Getting SDEK Delivery Point Module=======================
					order_item_array=[]
					order_items=OrderItem.objects.filter(order=order)
					#====================Cart Module==============================
					#confirmation from Y-kassa does not see if the user is authorized or not. Consequently if can not select
					#a cart sinsce the cart is selected either based on the user or session key. Confirmatin function does not
					#see neither & creates a new sessison key. That's why we save the cart in order_items model.              
					for item in order_items:
						if CartItem.objects.filter(product=item.product, cart=item.cart).exists():
							cart_item=CartItem.objects.get(product=item.product, cart=item.cart)
							cart_item.quantity=cart_item.quantity-item.quantity
							if cart_item.quantity<=0:
								cart_item.delete()
							else:
								cart_item.save()
						else:
							print('No cart_item corresponds to the order_item')
				#===================End of Cart Module=========================
				#=======Making order_items array for further using it in SDEK order=======================			
						product=Product.objects.get(article=item.article)
						sku=product.ozon_sku
						order_item_dict={
								'name': item.product,
								'ware_key': item.article,
								'payment': {
									"value": 0,
									"vat_sum": 0,
									"vat_rate": 0,
									},
								"weight": 800,
								"amount": 1,
								"cost": 1,
							}
						order_item_array.append(order_item_dict)
				#==============End of Making order_items arrary=====================
        #==============Creating an RHO=========================================
						if RemainderHistory.objects.filter(article=item.article, created__lt=dateTime).exists():
							rhos=RemainderHistory.objects.filter(article=item.article, created__lt=dateTime)
							rho_latest=rhos.latest('created')
							pre_remainder=rho_latest.current_remainder
						else:
							pre_remainder=0
							#rint(pre_remainder)
						rho=RemainderHistory.objects.create(
						rho_type=doc_type,
						created=dateTime,
						article=product.article,
						ozon_id=product.ozon_id,
						ozon_sku=sku,
						name=product.name,
						status='initiated by auto-deflector.ru',
						shipment_id=order.id,
						pre_remainder=pre_remainder,
						incoming_quantity=0,
						outgoing_quantity=int(item.quantity),
						current_remainder=pre_remainder - int(item.quantity),
						retail_price=int(product.site_retail_price),
						total_retail_sum=int(item.quantity) * int(product.site_retail_price),
						)
						#editing current quatityt in product table for future reports
						#taking current qunatity report based on rho table takes too much time
						product.quantity=rho.current_remainder
						product.total_sum=rho.current_remainder * product.av_price
						product.save()

				#=====================Creating sdek shipment order========================
					sdek_order={
						"type": 1,
						# "additional_order_types": [],
						"number": order.id,
						# "accompanying_number": "string",
						"tariff_code": 136,
						# "comment": "string",
						"shipment_point": "NN8",
						"delivery_point": delivery_point.code,
						# "date_invoice": "2019-08-24",
						# "shipper_name": "string",
						# "shipper_address": "string",
						# "delivery_recipient_cost":{
						#     "value": delivery_cost,
						#     "vat_sum": 0,
						#     "vat_rate": 0,
						#     },
						# "delivery_recipient_cost_adv": [],
						# "sender": {},
						# "seller": {},
						"recipient":{
							# "company": "string",
							"name": contragent_full_name,
							# "contragent_type": "INDIVIDUAL",
							# "passport_series": "string",
							# "passport_number": "string",
							# "passport_date_of_issue": "2019-08-24",
							# "passport_organization": "string",
							# "tin": "string",
							# "passport_date_of_birth": "2019-08-24",
							"email": order.receiver_email,
							"phones": [
							{'number': order.receiver_phone, },]
							},
						# "from_location": {},
						# "to_location": {},
						# "services": [],
						"packages": [
							{
							"number": order.id,
							"weight": 1000,
							"length": 100,
							"width": 30,
							"height": 5,
							"comment": "Хрупкое, обращаться осторожно",
							"items":  order_item_array,
							}
							],
						# "is_client_return": true,
						# "has_reverse_order": true,
						# "developer_key": "string",
						# "print": "WAYBILL",
						# "widget_token": "string"
						}
					print('===================Getting Auth Token for SDEK========================')
					url="https://api.cdek.ru/v2/oauth/token"
					headers = {
						"grant_type": "client_credentials",
						"client_id": "xJ8eEVHHhkFivswDPikl6MEOSv3Xz4y8",
						"client_secret": "UGAs5SsIJChB0SetwSabYHAocKCRaTdV"
					}
					response = requests.post(url, params=headers,)
					json=response.json()
					access_token=json['access_token']
					print(access_token)
					print('=================Successfull Getting of Auth Token for SDEK========================')
					headers = {
						"Authorization": f'Bearer {access_token}',
					}
					print('=========================Creating SDEK Order========================')
					url="https://api.cdek.ru/v2/orders"
					response = requests.post(url, headers=headers, json=sdek_order)
					print(response.status_code)
					json=response.json()
					print("Respone from SDEK API: ")
					print(json)
					print('=====================Successfull Creation of SDEK order===========================')
                    
					#===============================	
					#two ways to get dict key value
					entity=json['entity']
					#entity=json.get('entity')
					uuid=entity['uuid']
					#uuid=entity.get('uuid')
					order.delivery_order_uuid=uuid
					order.save()
		except Exception as e:
			print(e)


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


#===========================================================
#Yandex market в качестве sku используеут артикул

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
  a=a['result']
  # a=a['id']
  # a=a['name']
  a=a['children']

  # print(a)

  # for key, value in a.items():
    #print(f"{key}")
  for i in a:
    for key, value in i.items():
      print(f"{key}: {value}")
      print('------------------------------------')
    print('===========================================')

def yandex_id(request):
  url=f'https://api.partner.market.yandex.ru/v2/campaigns'
  headers = {"Api-Key": "ACMA:lRqnoRHucSnmiG7kCDWEXVtYe99fBQN2obEHsYCR:21dc8ee9"}
  response = requests.get(url, headers=headers)
  status_code=response.status_code
  print(status_code)
  a=response.json()
  print(a)

#Yandex market uses articles as skus
def yandex_update_prices(request):
    products=Product.objects.all()
    businessId='216409363'
    body_list=[]
    url=f'https://api.partner.market.yandex.ru/v2/businesses/{businessId}/offer-prices/updates'
    headers = {"Api-Key": "ACMA:lRqnoRHucSnmiG7kCDWEXVtYe99fBQN2obEHsYCR:21dc8ee9"}

    for product in products:
        price_dict ={
            'offerId' : product.article,
            'price': {
                'value' : 2790,
                'currencyId': "RUR",
                'discountBase': 3990,
                "minimumForBestseller": 2700
            }
        }
        body_list.append(price_dict)



    params = {'offers': body_list}
    response = requests.post(url, json=params, headers=headers)
    status_code=response.status_code
    print(status_code)
    print('========================')
    a=response.json()
    print(response)
    print('========================')
    print(a)

#показывает среднюю цена на площадке на аналогичный товар и кол-во показов за последние 7 дней (параметр "show")
def yandex_price_recommendations (request):
    products=Product.objects.all()
    businessId='216409363'
    body_list=[]
    url=f'https://api.partner.market.yandex.ru/v2/businesses/{businessId}/offers/recommendations'
    headers = {"Api-Key": "ACMA:lRqnoRHucSnmiG7kCDWEXVtYe99fBQN2obEHsYCR:21dc8ee9"}

    for product in products:
        body_list.append(product.article)

    params = {
        "offerIds": body_list,
        "competitivenessFilter": "AVERAGE"
    }

    response = requests.post(url, json=params, headers=headers)
    status_code=response.status_code
    print(status_code)
    a=response.json()
    print(response)
    # print(a)
    # print('===========================')
    a=a['result']
    # print(a)
    # print('==============================')
    a=a['offerRecommendations']
    # print(a)
    # print('+++++++++++++++++++++++++++++')
    n=0
    for i in a:
       n+=1
       item=i['offer']
       recommendation=i['recommendation']
       print(n, item)
       print(recommendation)
       print()
    #    print(f"SKU: {item['offerID']}; Price: {item['price']['value']}; Status: {item['price']['value']}")

def yandex_update_quantities(request):
    pass

