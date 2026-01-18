from django.shortcuts import render, redirect
import requests
from app_reference.models import SDEK_Office, SDEK_City
from app_purchase.models import Order, OrderItem
from django.contrib import messages, auth
import time


#для работы с методами необходимо получить "Bearer Token". 
#Для того, чтобы его полчить нужны "client_id" и "client_secret". Берем их из ЛК СДЕК.
#Время жизни токена: 3599 секунд (1 мин), поэтому каждый раз получаем новый
def get_list_of_sdek_offices (request):
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
    return redirect ('shopfront')

def get_list_of_sdek_cities(request):
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
    print('============================')
    print(json)
    access_token=json['access_token']
  
    headers = {
        "Authorization": f'Bearer {access_token}',
    }
    url="https://api.cdek.ru/v2/location/cities"
    #headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}
    response = requests.get(url, headers=headers)
    json=response.json()
    for i in json:
        if SDEK_City.objects.filter(code=i['code']).exists():
            city=SDEK_City.objects.get(code=i['code'])
            city.name=i['city'],
            city.region=i['region'],
            city.city_uuid=i['city_uuid'],
            longitude=i['longitude'],
            latitude=i['latitude'],
            country_code=i['country_code'],
        city_items=SDEK_City.objects.create(
            code=i['code'],
            name=i['city'],
            region=i['region'],
            city_uuid=i['city_uuid'],
            longitude=i['longitude'],
            latitude=i['latitude'],
            country_code=i['country_code'],
        )
        print(i)
        print()
   

    return redirect ('shopfront')

def get_list_of_sdek_locations(request):
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
    print('============================')
    print(json)
    access_token=json['access_token']
  
    headers = {
        "Authorization": f'Bearer {access_token}',
    }
    url="/v2/location/suggest/cities"
    #headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}
    response = requests.get(url, headers=headers)
    json=response.json()
    print(json)

def get_list_of_sdek_tariffs(request):
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
    print('============================')
    print(json)
    access_token=json['access_token']
  
    headers = {
        "Authorization": f'Bearer {access_token}',
    }
    url="https://api.cdek.ru/v2/calculator/alltariffs"
    #headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}
    response = requests.get(url, headers=headers)
    json=response.json()
    list=json['tariff_codes']
    print('List of tariffs: ')
    for i in list:
        print('===============')
        print(i)

#========================================================

#tariffs   
def get_sdek_delivery_cost(request):
    if request.method == 'POST':
        shipment_city=request.POST["shipment_city"]
        shipment_region=request.POST["shipment_region"]
        print('======================================')
        print(shipment_region, shipment_city)
        city=SDEK_City.objects.get(name=shipment_city, region=shipment_region)

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
        print('============================')
        # print(json)
        access_token=json['access_token']
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
                        'code' : city.code,
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
        #url="https://api.cdek.ru/v2/calculator/tarifflist"
        #headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}
        response = requests.post(url, headers=headers, json=params)
        json=response.json()
        delivery_cost=json['delivery_sum']
        # print('=======================')
        # data=response.json()
        # a=data['tariff_codes']
        # for i in a:
        #     if i['tariff_code'] == 136:
        #         print(i)
        #         delivery_sum=i['delivery_sum']
        #         break
        # delivery_cost= int(delivery_sum)
        
        context = {
            'delivery_cost': delivery_cost,
            'shipment_city' : shipment_city,
            # 'order': order,
        }
        return render (request, 'delivery/delivery_cost.html' , context)

#======================================================
def delivery_city_choice(request):
    if request.method=="POST":
        country=request.POST.get('country', False)
        region=request.POST.get('region', False)
        city=request.POST.get('city', False)
        countries=['Россия', 'Казахстан', 'Белоруссия']
        if country and region:
            # print(country, region, city)
            if country=="Россия":
                country_code="RU"
            elif country=="Казахстан":
                country_code='KZ'
            else:
                country_code="BY"
            regions=SDEK_Office.objects.filter(country_code=country_code)
            regions=regions.distinct('region')
            cities=SDEK_Office.objects.filter(region=region)
            cities=cities.distinct('city')
            context = {
                'countries': countries,
                'regions': regions,
                'cities': cities
            }
            
            return render (request, 'delivery/delivery_city_choice.html', context )
        
        elif country:
            # print(country)
            if country=="Россия":
                country_code="RU"
            elif country=="Казахстан":
                country_code='KZ'
            else:
                country_code="BY"
            
            regions=SDEK_Office.objects.filter(country_code=country_code)
            regions=regions.distinct('region')
          
            context = {
                'countries': countries,
                'regions': regions,
                #'cities': cities,
            }
            return render(request, 'delivery/delivery_city_choice.html', context)

    else:
        countries=['Россия', 'Казахстан', 'Белоруссия']
        # sdek_offices=SDEK_Office.objects.filter(country_code__in=['KZ', 'RU', 'BY']).order_by('-country_code')
        context = {
            'countries': countries,
        }
        return render (request, 'delivery/delivery_city_choice.html', context )

#функция, которая сначала подставляет СТРАНУ, потом РЕГИОН, потом ГОРОД
#основная для выбора пункта доставки
#использует таблицу app.reference SDEK_Office
def sdek_office_choice(request, order_id):
    order=Order.objects.get(id=order_id)
    order_items=OrderItem.objects.filter(order=order)
    if request.method=="POST":
        country=request.POST.get('country', False)
        region=request.POST.get('region', False)
        city=request.POST.get('city', False)
        countries=['Россия', 'Казахстан', 'Белоруссия']
        if country and region and city:
            print(country, region, city)
            if country=="Россия":
                country_code="RU"
            elif country=="Казахстан":
                country_code='KZ'
            else:
                country_code="BY"
            regions=SDEK_Office.objects.filter(country_code=country_code, type='PVZ')
            regions=regions.distinct('region')
            cities=SDEK_Office.objects.filter(region=region)
            cities=cities.distinct('city')

            offices=SDEK_Office.objects.filter(country_code=country_code, region=region, city=city, type='PVZ').order_by('address_full')
            if request.user.is_authenticated:
                context = {
                    'order': order,
                    'order_items': order_items,
                    'countries': countries,
                    'regions': regions,
                    'cities' : cities,
                    'offices': offices,
                    'f_name': order.user.first_name,
                    'l_name': order.user.last_name,
                    'email': order.user.email,
                }
                return render(request, 'cart/order_page.html', context)
            else:
                context = {
                    'order': order,
                    'order_items': order_items,
                    'countries': countries,
                    'regions': regions,
                    'cities' : cities,
                    'offices': offices,
                }
                return render(request, 'cart/order_page.html', context)

        elif country and region:
            print(country, region)
            if country=="Россия":
                country_code="RU"
            elif country=="Казахстан":
                country_code='KZ'
            else:
                country_code="BY"
            regions=SDEK_Office.objects.filter(country_code=country_code, type='PVZ')
            regions=regions.distinct('region')
            cities=SDEK_Office.objects.filter(region=region, type='PVZ')
            cities=cities.distinct('city')
            if request.user.is_authenticated:
                context = {
                'order': order,
                'order_items': order_items,
                'countries' : countries,
                'regions': regions,
                'cities' : cities,
                'f_name': order.user.first_name,
                'l_name': order.user.last_name,
                'email': order.user.email,
                }
                return render(request, 'cart/order_page.html', context)
            else:
                context = {
                    'order': order,
                    'order_items': order_items,
                    'countries': countries,
                    'regions': regions,
                    'cities' : cities,
                }
                return render(request, 'cart/order_page.html', context)
        elif country:
            print(country)
            if country=="Россия":
                country_code="RU"
            elif country=="Казахстан":
                country_code='KZ'
            else:
                country_code="BY"
            
            regions=SDEK_Office.objects.filter(country_code=country_code, type='PVZ')
            regions=regions.distinct('region')

            if request.user.is_authenticated:
                context = {
                'order': order,
                'order_items': order_items,
                'regions': regions,
                'countries' : countries,
                'f_name': order.user.first_name,
                'l_name': order.user.last_name,
                'email': order.user.email,
                }
                return render(request, 'cart/order_page.html', context)
            else:
                context = {
                    'countries': countries,
                    'order': order,
                    'order_items': order_items,
                    'regions': regions,
                    #'cities': cities,
                }
                return render(request, 'cart/order_page.html', context)
        else:
            countries=['Россия', 'Казахстан', 'Белоруссия']
            if request.user.is_authenticated:
                context = {
                    'order': order,
                    'order_items': order_items,
                    'countries' : countries,
                    'f_name': order.user.first_name,
                    'l_name': order.user.last_name,
                }
                return render(request, 'cart/order_page.html', context)
            else:
                context = {
                    'order': order,
                    'order_items': order_items,
                    'countries' : countries,
                    'order_id' : order_id,
                }
            return render(request, 'cart/order_page.html', context)
    else:
        countries=['Россия', 'Казахстан', 'Белоруссия']
        if request.user.is_authenticated:
            context = {
                'order': order,
                'order_items': order_items,
                'countries' : countries,
                'f_name': order.user.first_name,
                'l_name': order.user.last_name,
                'email': order.user.email,
            }
            return render(request, 'cart/order_page_final.html', context)
        else:
            context = {
                'order': order,
                'order_items': order_items,
                'countries' : countries,
            }
            return render(request, 'cart/order_page_final.html', context)

#======================================================
def create_sdek_shipment (request, order_id):
    order=Order.objects.get(id=order_id)
    order_items=OrderItem.objects.filter(order=order)

    if request.method=='POST':
        shipment_office = request.POST["shipment_office"]
        if shipment_office:
            print(shipment_office)
        else:
            messages.error(request,"Вы не ввели пункт выдачи сдек")
            return redirect ('sdek_office_choice', order.id)
        if SDEK_Office.objects.filter(address_full=shipment_office).exists():
            shipment_office=SDEK_Office.objects.get(address_full=shipment_office)
            city_code=shipment_office.city_code
            
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

            params= {
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
                        "length": 140,
                        "width": 30,
                        "height": 5
                        },
                    ]
    
                }

            url="https://api.cdek.ru/v2/calculator/tarifflist"
            response = requests.post(url, headers=headers, json=params)
            json=response.json()
            a=json['tariff_codes']
            for i in a:
                if i['tariff_code'] == 136:
                    print(i)
                    delivery_sum=i['delivery_sum']
                    break
            sum_to_pay= int(delivery_sum) + int(order.sum)
            context = {
                'sum_to_pay': sum_to_pay,
                'delivery_sum': delivery_sum,
                'shipment_office' : shipment_office,
                'order': order,
                'order_items': order_items
            }
            return render (request, 'cart/shipment.html' , context)
        else:
            messages.error(request,"Вы не ввели полностью необдходимые данные.")
            return redirect ('order', order.id)   

#========================================================
def get_order_status (request):
    #getting valid bearer token
    if request.method=="POST":
        uuid=request.POST["uuid"]
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

    #uuid='02d1c0f4-d1af-445c-82bb-7f24a2854f1d'
    # params= {
    #     'uuid': uuid
    # }
    url=f'https://api.cdek.ru/v2/orders/{uuid}'
    response = requests.get(url, headers=headers,)
    #response = requests.get(url, headers=headers, json=params)
    json=response.json()
    print(json)

#=======================================================
def open_sdek_vidget(request):
    return render (request, 'cart/sdekvidget_ver_1.html' )

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
    params = {
        "type": 1, 
        "number": '2561',
        "tariff_code": 136,
        "shipment_point": 'NN8',
        "delivery_point": 'PKR1',
        "recipient": {'name': "Винокуров Сергей Николаевич",
                      'contragent_type': 'INDIVIDUAL',
                      'phones': [{'number': '+79506204465'}],
                    },  
        "packages": [{
                        "number": "1225",
                        "weight": 1000,
                        "length": 140,
                        "width": 30,
                        "height": 5,
                        "items":[{
                            "name": "Deflector Chevrolet Lacetti",
                            'ware_key': 'DK-IN-00025',
                            "payment": {
                                "value": 0,
                                "vat_sum": 0,
                                "vat_rate": 'null'
                                },
                            'weight': 1000,
                            'amount': 1,
                            'cost': 1
                             
                        }],
                    }]
    }                  

    url="https://api.cdek.ru/v2/orders"
    response = requests.post(url, headers=headers, json=params)
    json=response.json()
    print(json)
    uuid=json['entity']['uuid']
    print(uuid)
    time.sleep(3)

    print('===========================')
    url=f'https://api.cdek.ru/v2/orders/{uuid}'
    response = requests.get(url, headers=headers,)
    #response = requests.get(url, headers=headers, json=params)
    json=response.json()
    print(json)

    return render (request, 'cart/payment_page.html')    