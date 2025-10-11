from django.shortcuts import render, redirect
import requests
from .models import AutoBrand, AutoModel, AutoModification


# Create your views here.
def load_auto_brands(request):
    headers = {
                "Client-Id": "1711314",
                "Api-Key": 'b54f0a3f-2e1a-4366-807e-165387fb5ba7'
            }
    
    task = {
        "attribute_id": 22916,
        "description_category_id": 17028755,
        "language": "DEFAULT",
        "last_value_id": 0,
        "limit": 1000,
        "type_id": 97593
    }
    response=requests.post('https://api-seller.ozon.ru/v1/description-category/attribute/values', json=task, headers=headers)
    status_code=response.status_code
    a=response.json()
    items_list=a['result']
    for i in items_list:
        if AutoBrand.objects.filter(ozon_attribute_id=i['id']).exists():
            continue
        item=AutoBrand.objects.create (
            ozon_attribute_id=i['id'],
            ozon_attribute_value=i['value']
        )

    return redirect ('dashboard')

def load_auto_models(request):
    headers = {
                "Client-Id": "1711314",
                "Api-Key": 'b54f0a3f-2e1a-4366-807e-165387fb5ba7'
            }
    
    task = {
        "attribute_id": 22917,
        "description_category_id": 17028755,
        "language": "DEFAULT",
        "last_value_id": 0,
        "limit": 5000,
        "type_id": 97593
    }
    response=requests.post('https://api-seller.ozon.ru/v1/description-category/attribute/values', json=task, headers=headers)
    status_code=response.status_code
    a=response.json()
    items_list=a['result']
    for i in items_list:
        if AutoModel.objects.filter(ozon_attribute_id=i['id']).exists():
            continue
        item=AutoModel.objects.create (
            ozon_attribute_id=i['id'],
            ozon_attribute_value=i['value'],
            ozon_attribute_info=i['info']
        )

    return redirect ('dashboard')
        
def load_auto_modifications(request):
    headers = {
                "Client-Id": "1711314",
                "Api-Key": 'b54f0a3f-2e1a-4366-807e-165387fb5ba7'
            }
    
    task = {
        "attribute_id": 22918,
        "description_category_id": 17028755,
        "language": "DEFAULT",
        "last_value_id": 0,
        "limit": 5000,
        "type_id": 97593
    }
    response=requests.post('https://api-seller.ozon.ru/v1/description-category/attribute/values', json=task, headers=headers)
    status_code=response.status_code
    a=response.json()
    items_list=a['result']
    for i in items_list:
        if AutoModification.objects.filter(ozon_attribute_id=i['id']).exists():
            continue
        item=AutoModification.objects.create (
            ozon_attribute_id=i['id'],
            ozon_attribute_value=i['value'],
            ozon_attribute_info_mod=i['info']
        )

    return redirect ('dashboard')