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
        item=AutoBrand.objects.create (
            ozon_attribute_id=i['id'],
            ozon_attribute_value=i['value']
        )

    return redirect ('dashoard')
        
      