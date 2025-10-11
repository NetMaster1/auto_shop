from django.shortcuts import render, redirect
import requests
from app_reference.models import SDEK_Office, SDEK_City
from app_purchase.models import Order

# Create your views here.


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
    print('============================')
    print(json)
    access_token=json['access_token']
  
    headers = {
        "Authorization": f'Bearer {access_token}',
    }
    
    url="https://api.cdek.ru/v2/deliverypoints"
    #headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}
    response = requests.get(url, headers=headers)
    json=response.json()
    offices=SDEK_Office.objects.all()
    for i in json:
        code=i['code']
        if SDEK_Office.objects.filter(code=code).exists():
            continue
        location=i['location']
        region=location['region']
        city=location['city']
        address_full=location['address_full']
        country_code=location['country_code']

        office =SDEK_Office.objects.create(
            code=code,
            address_full = address_full,
            country_code=country_code,
            region = region,
            city = city,
        )

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

def get_sdek_delivery_cost(request):
    if request.method=='POST':
        sender_city = request.POST["sender_city"]
        receiver_city = request.POST["receiver_city"]
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

        params= {

            "from_location" : "sdfsdfs"
        
        }
        url="https://api.cdek.ru/v2/calculator/tarifflist"
        #headers = {"Authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc2MDM0Nzg4NywiaWQiOiIwMTk2MzExMC04MmJiLTdjMGEtYTEzYy03MjdmMjY5NzVjZWEiLCJpaWQiOjEwMjIxMDYwMCwib2lkIjo0MjQ1NTQ1LCJzIjo3OTM0LCJzaWQiOiJkZDQ2MDQ1Mi03NWQzLTQ0OTktOWU4OC1jMjVhNTE1NzBhNzIiLCJ0IjpmYWxzZSwidWlkIjoxMDIyMTA2MDB9.srXrKwyCJCH_nZAzKi4PaT6pueamPhwz-hqBYP7l--UafAd0gmNTSr7xoNWxFmN1S65kG-2WBUA_l0qrYaDGvg"}
        response = requests.pot(url, headers=headers)
        json=response.json()
        print(json)


def sdek_country_choice(request, order_id):
    if request.method=="POST":
        order=Order.objects.get(id=order_id)

        country=request.POST.get('country', False)
        region=request.POST.get('region', False)
        city=request.POST.get('city', False)
        countries=['Россия', 'Казахстан', 'Белоруссия']
        if country:
            print(country)
            if country=="Россия":
                country_code="RU"
            elif country=="Казахстан":
                country_code='KZ'
            else:
                country_code="BY"
            
            regions=SDEK_Office.objects.filter(country_code=country_code)
            context = {
                'countries': countries,
                'order': order,
                'regions': regions
                }
            return render(request, 'cart/order_page.html', context)

        if region:
            print(region)
            cities=SDEK_Office.objects.filter(region=region)
            context = {
                'order': order,
                'country': country,
                'regions': regions
            }
            return render(request, 'cart/order_page.html', context)

        context = {
            'order': order,
            'country': country,
            # 'regions': regions
        }
    return render(request, 'cart/order_page.html', context)