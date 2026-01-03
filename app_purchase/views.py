from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from . models import Cart, CartItem, Identifier, OrderItem, Order, Customer
from app_product.models import Product
from app_reference.models import SDEK_Office
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
import uuid
from yookassa import Configuration, Payment
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages, auth
import time
import requests
import json
from decimal import Decimal


# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, id):
    product=Product.objects.get(id=id)
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        #cart=Cart.objects.get(cart_id=request.session)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        #cart = Cart.objects.create(cart_id=request.session)
        #cart.save()
    try:
        cart_item = CartItem.objects.get(product=product.name, cart=cart)
        cart_item.quantity+=1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product.name,
            article=product.article,
            image=product.image_1,
            cart=cart,
            quantity=1,
            price=product.site_retail_price,
        )

    return redirect('cart_detail')

def cart_detail(request):
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        #cart=Cart.objects.get(cart_id=request.session)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))

    cart=Cart.objects.get(cart_id=cart)
    cart_items=CartItem.objects.filter(cart=cart).order_by('product')
    total=0
    for item in cart_items:
        sub_total=item.quantity*item.price
        total+=sub_total
        
    context = {
        'cart_items' : cart_items,
        'total': total,
        'cart': cart,
    }

    return render (request, 'cart/cart.html', context)

def add_cart_item(request, id):
    cart_item=CartItem.objects.get(id=id)
    cart_item.quantity+=1
    cart_item.save()
    return redirect ('cart_detail')

def remove_cart_item(request, id):
    cart_item=CartItem.objects.get(id=id)
    if cart_item.quantity > 1:
        cart_item.quantity-=1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect ('cart_detail')

def delete_cart_item(request, id):
    cart_item=CartItem.objects.get(id=id)
    cart_item.delete()
    return redirect ('cart_detail')

def purchase_product(request):
    if request.method == "POST":
        check_boxes=request.POST.getlist("checkbox", None)
        identifier=Identifier.objects.create()
        order=Order.objects.create()
        if request.user.is_authenticated:
            order.user=request.user
            order.save()
        for value in check_boxes:
            cart_item=CartItem.objects.get(id=value)
            order_item=OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                article=cart_item.article,
                image=cart_item.image,
                price=cart_item.price,
                quantity=cart_item.quantity,
                sub_total=cart_item.price*cart_item.quantity,

            )
        order_items=OrderItem.objects.filter(order=order).order_by('product')
       
        sum=0
        for item in order_items:
            sum+=item.sub_total
        order.sum=sum
        order.save()
        return redirect ('order',  order.id)
    
def order(request, order_id):
    countries=['Россия', 'Казахстан', 'Белоруссия']
    # sdek_offices=SDEK_Office.objects.filter(country_code__in=['KZ', 'RU', 'BY']).order_by('-country_code')

    order=Order.objects.get(id=order_id)
    order_items=OrderItem.objects.filter(order=order)
    if request.user.is_authenticated:
        f_name=order.user.first_name
        l_name=order.user.last_name
        email=order.user.email

        context = {
            'order': order,
            'order_items': order_items,
            'countries': countries,
            'f_name': f_name,
            'l_name': l_name,
            'email': email,
            # 'sdek_offices': sdek_offices,
            }
        return render (request, 'cart/order_page.html', context)
    
    else:
        context = {
            'order': order,
            'order_items': order_items,
            'countries': countries,
            # 'sdek_offices': sdek_offices,
        }

        return render (request, 'cart/order_page.html', context)
 
def create_final_purchase_order(request, order_id):
    if request.method=='POST': 
        order=Order.objects.get(id=order_id)
        order_items=OrderItem.objects.filter(order=order)
        shipment_office = request.POST["shipment_office"]
        f_name = request.POST["f_name"]
        l_name = request.POST["l_name"]
        phone = request.POST["phone"]
        email = request.POST["email"]
        
        office=SDEK_Office.objects.get(address_full=shipment_office)
        city_code=office.city_code
        try:
            print('=================Getting Valid Bearer Token for SDEK====================')
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
            print(f'Access token: {access_token}')
            print('=======================Successfull getting of access token===============================')
            print('============Getting delivery cost=====================')
            headers = {
                "Authorization": f'Bearer {access_token}',
            }
            params= {
                
                        "tariff_code": 136,
                        "from_location" : {
                            'code': 414,
                            'contragent_type': 'LEGAL_ENTITY'
                            },
                        "to_location" : {
                            'code' : city_code,
                            'contragent_type': 'INDIVIDUAL',
                            },
                        "packages": [
                            {   "weight": 1000,
                                "length": 100,
                                "width": 30,
                                "height": 5
                                },
                            ]
                    }
            url="https://api.cdek.ru/v2/calculator/tariff"
            #headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}
            response = requests.post(url, headers=headers, json=params)
            json=response.json()
            print(json)
            print('=============Successfull getting of delivery cost=======================')
            delivery_cost= json['delivery_sum']
            #converting float to string for further converting the string to decimal since python does not support float.
            #It supports decimal and ykassa API uses float
            delivery_cost=str(delivery_cost)
            delivery_cost=Decimal(delivery_cost)
    #=======================End of getting delivery cost====================

            order.delivery_point=shipment_office
            order.receiver_firstName=f_name
            order.receiver_lastName=l_name
            order.receiver_phone=phone
            order.receiver_email=email
            order.delivery_cost=delivery_cost
            order.bill=delivery_cost + order.sum
            order.save()
            print (order.sum)
            print(order.delivery_cost)
            print(order.bill)
            print (type(order.sum))
            print (type(order.bill))
            print (type(order.delivery_cost))
            
            context ={
                "order": order,
                "order_items": order_items,
            }

            return render (request, 'cart/order_page_final.html', context)
        except:
            messages.error(request,"Не удалось получить стоимость доставки. Попробуйте еще раз.")
            return redirect("order", order.id)
    
#========================ю-касса====================================
def make_payment(request, order_id):
    order=Order.objects.get(id=order_id)
    order_items=OrderItem.objects.filter(order=order)
    items_arr=[]
    item_dict={}

    item_cost=0
    for item in order_items:
        item_cost+=item.sub_total
        item_dict={
            "description": item.product,
            "quantity": item.quantity,
            "amount": {
                "value": item.price,
                "currency": "RUB"
                },
            "vat_code": 1,
            "payment_mode": "full_prepayment",
            "payment_subject": "commodity",
        }
        items_arr.append(item_dict)
   
    item_dict={
            "description": 'delivery',
            "quantity": 1,
            "amount": {
                "value": order.delivery_cost,
                "currency": "RUB"
                },
            "vat_code": 1,
            "payment_mode": "full_prepayment",
            "payment_subject": "commodity",
        }
    items_arr.append(item_dict)
    Configuration.account_id = '1159072'#shop id
    Configuration.secret_key = 'live_lJQG_JqI1j3k2DicZikQHWd08Pp4YUSDADS7zZo_4i0'#API Key
    payment = Payment.create({
        "amount": {
                "value": order.bill,
                #"value": str(item_cost),
                "currency": "RUB"
                },
        "receipt": {
            "customer": {
                #"email": order.buyer.f_name,
                "email": '79200711112@yandex.ru',
                },
                "items": items_arr,
                },          
        "confirmation": {
            "type": "redirect",
            "return_url": "https://www.auto-deflector.ru"
            },
        "capture": True,
        "description": order.id,
    },
    uuid.uuid4())
    return HttpResponseRedirect(payment.confirmation.confirmation_url)


    