from django.shortcuts import render
from rest_framework import viewsets
from .models import ServerResponse
from .serializers import ServerResponseSerializer

# Create your views here.


class ServerResponseView(viewsets.ModelViewSet):
    queryset=ServerResponse.objects.all()
    serializer_class=ServerResponseSerializer