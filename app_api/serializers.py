from rest_framework import serializers
from .models import ServerResponse

class ServerResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model= ServerResponse
        fields = ('version', 'name')
        #fields = ('version', 'name', 'time')