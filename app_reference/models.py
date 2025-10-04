from django.db import models


class AutoBrand (models.Model):
    ozon_attribute_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    ozon_attribute_value = models.CharField(max_length=50, unique=True, null=True, blank=True)
    ozon_attribute_info = models.TextField(null=True, blank=True)
    ozon_attribute_picture = models.FileField(upload_to='uploads', null=True, blank=True)
    
    def __int__(self):
        return self.id
    
class AutoModel (models.Model):
    ozon_attribute_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    ozon_attribute_value = models.CharField(max_length=100, unique=True, null=True, blank=True)
    ozon_attribute_info = models.TextField(null=True, blank=True)
    ozon_attribute_picture = models.FileField(upload_to='uploads', null=True, blank=True)
    
    def __int__(self):
        return self.id
    
class AutoModification (models.Model):
    ozon_attribute_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    ozon_attribute_value = models.CharField(max_length=50, unique=True, null=True, blank=True)
    ozon_attribute_info = models.CharField(max_length=50, null=True, blank=True)
    ozon_attribute_picture = models.FileField(upload_to='uploads', null=True, blank=True)
    
    def __int__(self):
        return self.id
