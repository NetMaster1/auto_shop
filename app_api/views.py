from django.shortcuts import render, redirect
from rest_framework import viewsets
from .models import ServerResponse
from .serializers import ServerResponseSerializer
import json
import requests
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse

# Create your views here.


class ServerResponseView(viewsets.ModelViewSet):
  
    queryset=ServerResponse.objects.all()
    serializer_class=ServerResponseSerializer


@csrf_exempt #отключает защиту csrf
def ozon_push(request):
    if request.method == 'POST':
      #получение данных запроса POST в формате json
        data = json.loads(request.body)
        print(data)
        time = data.get("time")
        print (time)
        json_data = {
          "version": "python",
          "name": "3.13.1",
          "time": time
}
        return JsonResponse(json_data, safe=False)
    
    messages.success(request, data)   
    return redirect("dashboard")
