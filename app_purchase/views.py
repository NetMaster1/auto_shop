from django.shortcuts import render, redirect
from . models import Cart, CartItem, Identifier, OrderItem, Order, Customer
from app_product.models import Product
from app_reference.models import SDEK_Office
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
import uuid
from yookassa import Configuration, Payment
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
import json
from django.contrib import messages, auth
import time
import requests

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
        order.delivery_point=shipment_office
        order.receiver_firstName=f_name
        order.receiver_lastName=l_name
        order.receiver_phone=phone
        order.receiver_email=email
        order.save()
        context ={
            "order": order,
            "order_items": order_items,
        }

        return render (request, 'cart/order_page_final.html', context)
    
#========================ю-касса====================================
def make_payment(request, order_id):
    order=Order.objects.get(id=order_id)
    order_items=OrderItem.objects.filter(order=order)
    items_arr=[]
    item_dict={}

    for item in order_items:
        item_dict={
                        "description": item.product,
                        "quantity": item.quantity,
                        "amount": {
                            "value": item.sub_total,
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
                "value": order.sum,
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

@csrf_exempt #отключает защиту csrf
def payment_status(request):
     if request.method == 'POST':
        try:
            #получение данных запроса POST от стороннего сайта в формате json и преобразование данных в формат словаря Python
            data = json.loads(request.body)
            print ('=========================')
            print(data)
        except:
            print('some error')
  
   