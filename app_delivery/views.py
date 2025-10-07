from django.shortcuts import render, redirect
import requests

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
    print(json)