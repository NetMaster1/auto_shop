from django.shortcuts import render, redirect
from app_product.models import Product, ProductCategory, RemainderHistory
import pandas
import xlwt
from django.contrib import messages
import requests
import time
import os
import time

def db_correct(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            file = request.FILES["file_name"]
            df1 = pandas.read_excel(file)
            cycle = len(df1)
            for i in range(cycle):
                row = df1.iloc[i]#reads each row of the df1 one by one
                article=row.Article
                if Product.objects.filter(article=article).exists():
                    product=Product.objects.get(article=article)
                    product.name=row.Title
                    product.save()
                if RemainderHistory.objects.filter(article=article).exists():
                    rhos=RemainderHistory.objects.filter(article=article)
                    for rho in rhos:
                        rho.name=row.Title
                        rho.save()
            return redirect('dashboard')

    return redirect ('login_page')

def product_quant_correct(request):
    if request.user.is_authenticated:
        products=Product.objects.all()
        for product in products:
            if RemainderHistory.objects.filter(article=product.article).exists():
                rho_latest = RemainderHistory.objects.filter(article=product.article).latest('created')
                product.quantity=rho_latest.current_remainder
                product.total_sum=rho_latest.current_remainder*product.av_price
                product.save()
        messages.success(request, 'Product table quantity and total_sum changed')   
        return redirect("dashboard")  
    return redirect ('login_page')
        
def change_ozon_qnt_for_short_deflectors (request):
    # tdelta=datetime.timedelta(hours=3)
    # dT_utcnow=datetime.datetime.now(tz=pytz.UTC)#Greenwich time aware of timezones
    # dateTime=dT_utcnow+tdelta
    if request.user.is_authenticated:
        products=Product.objects.filter(length__lte=140)
        for product in products:
            article=product.article
            if RemainderHistory.objects.filter(article=article).exists():
                rhos=RemainderHistory.objects.filter(article=article)
                #rho_latest = RemainderHistory.objects.filter(article=article, created__lte=dateTime).latest("created")
                rho_latest = RemainderHistory.objects.filter(article=article).latest("created")
                current_remainder=rho_latest.current_remainder
                if product.ozon_id:
                    headers = {
                        "Client-Id": "1711314",
                        "Api-Key": 'b54f0a3f-2e1a-4366-807e-165387fb5ba7'
                    }
            
                    #update quantity of products at ozon warehouse making it equal to OOC warehouse
                    task = {
                        "stocks": [
                            {
                                "offer_id": str(product.article),
                                "product_id": str(product.ozon_id),
                                "stock": rho_latest.current_remainder,
                                #warehouse (Неклюдово)
                                "warehouse_id": 1020005000113280
                            }
                        ]
                    }
                    response=requests.post('https://api-seller.ozon.ru/v2/products/stocks', json=task, headers=headers)
                    print(response)
                    json=response.json()
                    #print(status_code)
                    print(json)
                    time.sleep(1)
        return redirect ('dashboard')
    return redirect ('login_page')

def create_list_of_files(request):
    files=os.listdir('DeflectorsDoor')
    category=ProductCategory.objects.get(name='Дефлектор двери')
    products=Product.objects.filter(category=category)
    for i in files:
        a=i.split('.')[0]
        for product in products:
            if a in product.name:
                product.image_1=i
                product.save()
                print(product.article)
                time.sleep(1)
    return redirect ('dashboard')
        
def rename_files(request):
    files=os.listdir('DeflectorsDoor')
    for i in files:
        os.rename(f'DeflectorsDoor/{i}', f'DeflectorsDoor/Дефлектор двери_{i}')
    return redirect ('dashboard')