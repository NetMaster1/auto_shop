from django.db import models

class LoginCounter (models.Model):
    user_name = models.CharField(max_length=50, null =True, blank=True)
    counter = models.IntegerField(default=0)
    
    def __int__(self):
        return self.id
    
