from django.conf import settings
#from app_items.models import Item
import datetime
import time
import requests
import json
import random
from app_product.models import Product, DocumentType, RemainderHistory
from app_reference.models import SDEK_Office
import pytz


def scheduled_dispatch():
	print('updater works')

def wb_synchronize_orders_with_ozon ():
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
    time.sleep(5)
    status_code=response.status_code
    print(status_code)
    # print(response)
    a=response.json()
    # print(a)
    print('================')
    orders_list=a['orders']
    print(orders_list)
    print('================')
    n=0
    for i in orders_list:
        print(i)
        order_id=i['id']
        n+=1
        sku=i['skus']
        sku=sku[0]
        if Product.objects.filter(wb_bar_code=sku).exists():
            product=Product.objects.get(wb_bar_code=sku)
            print('==============================')
            print(f"Order #{n} shipment_id: {i['id']}; sku: {sku}; name: {product.name}; article: {product.article}" )
        else:
            print('==============================')
            print(f"Order #{n} shipment_id: {i['id']}; sku: {sku}; name: No Name" )
            continue
        
        if RemainderHistory.objects.filter(shipment_id=order_id).exists():
            print(f"RHO with shipment_id: {i['id']} exists .")
            continue
        else:
            # tdelta=datetime.timedelta(hours=3)
            # dateTime=datetime.datetime.now()
            # dT_utcnow=datetime.datetime.now(tz=pytz.UTC)#Greenwich time aware of timezones
            # dateTime=dT_utcnow+tdelta

            current_dt=datetime.datetime.now()
            tdelta=datetime.timedelta(hours=3)
            mics=current_dt.microsecond
            tdelta_1=datetime.timedelta(microseconds=mics)
            secs=current_dt.second
            tdelta_2=datetime.timedelta(seconds=secs)
            tdelta_3=tdelta+tdelta_1+tdelta_2
            dateTime=current_dt+tdelta_3
            print(f"Order {i['id']} created at {dateTime}")
            
            if RemainderHistory.objects.filter(article=product.article, created__lt=dateTime).exists():
                # print("True")
                rho_latest_before = RemainderHistory.objects.filter(article=product.article,  created__lt=dateTime).latest('created')
                # print(rho_latest_before)
                # print(rho_latest_before.current_remainder)
                pre_remainder=rho_latest_before.current_remainder
            else:
                pre_remainder=0
                # print(pre_remainder)
            #time.sleep(1)
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
                current_remainder=pre_remainder - 1
                #retail_price=int(retail_price),
                # total_retail_sum=int(row.Retail_Price) * int(row.Qnty),
                )
            
            product.quantity=rho.current_remainder
            product.total_sum=rho.current_remainder * product.av_price
            product.save()
            # print('++++++++++++++++++++++++++++++++++++++++')
            # print('One cycle made')

            if product.ozon_id:
                stock_dict={
                    "offer_id": str(product.article),
                    "product_id": str(product.ozon_id),
                    "stock": rho.current_remainder,
                    #warehouse (Неклюдово)
                    "warehouse_id": 1020005000113280
                    }
                stock_arr.append(stock_dict)
                
        # if len(stock_arr) > 0:           
        #     for i in stock_arr:
        #         print (i)
        # else:
        #     print('stock_arr is empty')
        # print('')
        
    task={
        "stocks" : stock_arr
    }
    response=requests.post('https://api-seller.ozon.ru/v2/products/stocks', json=task, headers=headers_ozon)

def wb_update_prices_auto():
	#Товары, цены и скидки для них. Максимум 1 000 товаров. Цена и скидка не могут быть пустыми одновременно.
	#Максимум 10 запросов за 6 секунд для всех методов категории Цены и скидки на один аккаунт продавца
    url=f'https://discounts-prices-api.wildberries.ru/api/v2/upload/task'
    headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}
   
    task_arr=[]
    products=Product.objects.all()
    for product in products:
        if product.wb_id:
            wb_id=product.wb_id
            task_dict={
                    "nmID": int(wb_id),
                    # "price": int(retail_price),
                    "price": 3990,
                    "discount": 30
                }
            task_arr.append(task_dict)
  
    params={
        "data" : task_arr
    }
    response = requests.post(url, json=params, headers=headers)

#для работы с методами необходимо получить "Bearer Token". 
#Для того, чтобы его полчить нужны "client_id" и "client_secret". Берем их из ЛК СДЕК.
#Время жизни токена: 3599 секунд (1 мин), поэтому каждый раз получаем новый
def list_of_sdek_offices_update ():
    #getting valid bearer token
    url="https://api.cdek.ru/v2/oauth/token"

    headers = {
        "grant_type": "client_credentials",
		"client_id": "xJ8eEVHHhkFivswDPikl6MEOSv3Xz4y8",
		"client_secret": "UGAs5SsIJChB0SetwSabYHAocKCRaTdV"
    }
    #в качестве параметров (params) передаём заголовки (headers)
    response = requests.post(url, params=headers, )
    json=response.json()
    access_token=json['access_token']
    headers = {
        "Authorization": f'Bearer {access_token}',
    }
    url="https://api.cdek.ru/v2/deliverypoints"
    #headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}
    response = requests.get(url, headers=headers)
    json=response.json()
    # print('======================')
    # print(json)
    offices=SDEK_Office.objects.all()
    office_codes=[]
    country_codes=['RU', 'KZ', 'BY']
    for i in json:
        for c in country_codes:
            # if i['location']['country_code']==c and i['type']=='PVZ' and i['is_handout']==True:
            if i['location']['country_code']==c and i['type']=='PVZ' and i['is_handout']==True:
                # if i['type']=='PVZ' and i['is_handout']==True:
                office_codes.append(i['code'])
                print('===========================')
                print(i)
                code=i['code']
                type=i['type']
                location=i['location']
                city_code=location['city_code']
                if SDEK_Office.objects.filter(code=code).exists():
                    office=SDEK_Office.objects.get(code=code)
                    office.city_code=city_code
                    office.type=type
                    office.save()
                    continue
                region=location['region']
                city=location['city']
                address_full=location['address_full']
                country_code=location['country_code']

                office =SDEK_Office.objects.create(
                    code=code,
                    type=type,
                    address_full = address_full,
                    country_code=country_code,
                    region = region,
                    city = city,
                    city_code=city_code
                )
    #getting rid of closed offices
    offices=SDEK_Office.objects.all()
    print(office_codes)
    deleted=0
    for office in offices:
        if office.code in office_codes:
            continue
        else:
            deleted+=1
            office.delete()
    print(f'Total Number of Offices: {offices.count()}')
    print(f'Number of offices deleted: {deleted}')
  




