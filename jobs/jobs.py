from django.conf import settings
#from app_items.models import Item
import datetime
import time
import requests
import json
import random
from app_product.models import Product, DocumentType, RemainderHistory
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
    status_code=response.status_code
    a=response.json()
    orders_list=a['orders']
    n=0
    for i in orders_list:
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
        
        if RemainderHistory.objects.filter(shipment_id=order_id).exists():
            print(f'RHO with shipment_id: {i['id']} exists .')
            continue

        else:
            tdelta=datetime.timedelta(hours=3)
            dateTime=datetime.datetime.now()
            dT_utcnow=datetime.datetime.now(tz=pytz.UTC)#Greenwich time aware of timezones
            dateTime=dT_utcnow+tdelta
            print(f'Order {i['id']} created at {dateTime}')
          

            if Product.objects.filter(wb_bar_code=sku).exists():
                # print('ok')
                product=Product.objects.get(wb_bar_code=sku)
                article=product.article
            #     print(product.name)
            #     print(f'wb_bar_code: {product.wb_bar_code}')
                print(f'RHO for order {i['id']} created')
            else:
                print(f'RHO not created due to no WB_BAR_CODE')
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
    print('')
    print('')
    print('')
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
    # print('')
        
    # task={
    #     "stocks" : stock_arr
    # }
    # response=requests.post('https://api-seller.ozon.ru/v2/products/stocks', json=task, headers=headers_ozon)

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

    




