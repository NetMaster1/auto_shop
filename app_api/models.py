from django.db import models
from datetime import datetime, date
from django.utils import timezone

class ServerResponse (models.Model):
    version = models.CharField(max_length=50)
    name = models.CharField(max_length=160, null=True, blank=True)
    time = models.DateTimeField(auto_now=True)
  
    def __int__(self):
        return self.id