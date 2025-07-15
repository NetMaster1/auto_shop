from django.conf import settings
#from app_items.models import Item
import datetime
import time
import requests
import json
import random
from app_product.models import Product


def scheduled_dispatch():
	print('updater works')


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
                    "price": 2990,
                    "discount": 0
                }
            task_arr.append(task_dict)
  
    params={
        "data" : task_arr
    }
    response = requests.post(url, json=params, headers=headers)




