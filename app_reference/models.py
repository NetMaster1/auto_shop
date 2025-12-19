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
    
class SDEK_Office (models.Model):
    code = models.CharField(max_length=25, unique=True, null=True, blank=True)
    type = models.CharField(max_length=25, default="PVZ")
    address_full = models.CharField(max_length=250, null=True, blank=True)
    country_code = models.CharField(max_length=10, null=True, blank=True)
    postal_code = models.CharField(max_length=50, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    city_code = models.CharField(max_length=10, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
 
    def __int__(self):
        return self.id
    
class SDEK_City (models.Model):
    code = models.CharField(max_length=25, unique=True, null=True, blank=True)
    city_uuid = models.CharField(max_length=100, unique=True, null=True, blank=True)
    country_code = models.CharField(max_length=10, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    fias = models.CharField(max_length=100, null=True, blank=True)
    longitude = models.CharField(max_length=25, null=True, blank=True)
    latitude = models.CharField(max_length=25, null=True, blank=True)
 
    def __int__(self):
        return self.id



    

