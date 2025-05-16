from django.shortcuts import render, redirect
from rest_framework import viewsets
from .models import ServerResponse
from .serializers import ServerResponseSerializer
import json
import requests
from django.contrib import messages

# Create your views here.


class ServerResponseView(viewsets.ModelViewSet):
  
    queryset=ServerResponse.objects.all()
    serializer_class=ServerResponseSerializer

def receive_ozon_push_message(request):
    data = json.loads(request.body)#получение данных запроса POST в формате json

    
    messages.success(request, data)   
    return redirect("dashboard")
