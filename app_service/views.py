from django.shortcuts import render, redirect
from app_product.models import Product, ProductCategory, RemainderHistory, DocumentType
from app_purchase.models import Cart, CartItem
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
        sale=DocumentType.objects.get(name='Продажа ТМЦ')
        delivery=DocumentType.objects.get(name='Поступление ТМЦ')
        recognition=DocumentType.objects.get(name='Оприходование ТМЦ')
        taking_back=DocumentType.objects.get(name='Возврат ТМЦ')
        signing_off=DocumentType.objects.get(name='Списание ТМЦ')
        products=Product.objects.all()
        for product in products:
            if RemainderHistory.objects.filter(article=product.article).exists():
                rhos=RemainderHistory.objects.filter(article=product.article).order_by('created')
                for rho in rhos:
                    if rho.shipment_id:
                        if RemainderHistory.objects.filter(article=product.article, shipment_id=rho.shipment_id, created__lt=rho.created).exists():
                            rho.delete()
                            continue
                    if RemainderHistory.objects.filter(article=product.article, created__lt=rho.created).exists():
                        rho_latest_before=RemainderHistory.objects.filter(article=product.article, created__lt=rho.created).latest('created')
                        pre_remainder=rho_latest_before.current_remainder
                    else:
                        pre_remainder=0
                    rho.pre_remainder=pre_remainder               
                    if rho.rho_type==delivery:
                        rho.current_remainder=rho.pre_remainder + rho.incoming_quantity
                    elif rho.rho_type==sale:
                        rho.current_remainder=rho.pre_remainder - rho.outgoing_quantity
                    rho.save()
                
                rho_latest=RemainderHistory.objects.filter(article=product.article).latest('created')
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
    files=os.listdir('DeflectorsHood')
    category=ProductCategory.objects.get(name='Дефлектор капота')
    products=Product.objects.filter(category=category)
    for i in files:
        a=i.split('.')[0]
        print(a)
        for product in products:
            if a in product.name:
                product.image_1=i
                print('True')
                product.save()
                print(product.article)
                time.sleep(1)
    return redirect ('dashboard')
        
def rename_files(request):
    files=os.listdir('DeflectorsDoor')
    for i in files:
        os.rename(f'DeflectorsDoor/{i}', f'DeflectorsDoor/Дефлектор двери_{i}')
    return redirect ('dashboard')

def db_correct_model_names(request):
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
                    product.brand=row.AutoBrand
                    product.model_short=row.AutoModel
                    product.brand_rus=row.Russian_Brand
                    product.model_short_rus=row.Russian_Model
                    product.save()   
            return redirect('dashboard')

def delete_cart_items(request):
    cart_items=CartItem.objects.all()
    for item in cart_items:
        item.delete()
    return redirect ('shopfront')

def delete_carts(request):
    carts=Cart.objects.all()
    for item in carts:
        item.delete()
    return redirect ('shopfront')

def html_test(request):
    return render (request, 'html_test.html')