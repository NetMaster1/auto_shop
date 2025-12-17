from django.db import models
from datetime import datetime, date
from django.utils import timezone

class ProductCategory (models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
   
    def __int__(self):
        return self.id

class Product (models.Model):
    created = models.DateTimeField(auto_now=True)
    emumerator = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=160)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.DO_NOTHING, null=True, blank=True)
    auto_model = models.CharField(max_length=160, null=True, blank=True)
    brand=models.CharField(max_length=160, null=True, blank=True)#used for hashtags
    brand_rus=models.CharField(max_length=160, null=True, blank=True)#used for hashtags
    model_short=models.CharField(max_length=160, null=True, blank=True)#used for hashtags
    model_short_rus=models.CharField(max_length=160, null=True, blank=True)#used for hashtags
    bar_code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    article = models.CharField(max_length=50, unique=True, null=True, blank=True)
    ozon_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    ozon_sku = models.CharField(max_length=50, unique=True, null=True, blank=True)
    wb_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    wb_bar_code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    wb_true = models.BooleanField(default=True)#used to block certain items' quantities from synchronizing with wb
    ozon_true = models.BooleanField(default=True)#used to block certain items' quantities from synchronizing with ozon
    site_true = models.BooleanField(default=True)#used to block certain items' quantities from synchronizing with site
    update_true = models.BooleanField(default=True)#used to block certain items from updating
    ean = models.CharField(max_length=50, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    av_price = models.IntegerField(default=0)
    total_sum = models.IntegerField(default=0)
    ozon_retail_price = models.IntegerField(default=0)
    wb_retail_price = models.IntegerField(default=0)
    site_retail_price = models.IntegerField(default=0)
    length = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    #=================rating module================
    percent = models.CharField(max_length=50, default='0%')
    total = models.IntegerField(default=0)  # Общее число баллов
    quantity = models.IntegerField(default=0)  # Кол-во оценок
    av_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)  # average rating
    #===============================================
    transactions = models.IntegerField(default=0)#counter
    image_1 = models.FileField(upload_to='uploads', null=True, blank=True)
    image_2 = models.FileField(upload_to='uploads', null=True, blank=True)
    image_3 = models.FileField(upload_to='uploads', null=True, blank=True)
    image_4 = models.FileField(upload_to='uploads', null=True, blank=True)
    image_5 = models.FileField(upload_to='uploads', null=True, blank=True)
    image_6 = models.FileField(upload_to='uploads', null=True, blank=True)
    image_7 = models.FileField(upload_to='uploads', null=True, blank=True)
    video_1 = models.FileField(upload_to='uploads', null=True, blank=True)
    

    def __int__(self):
        return self.id
    
class DocumentType (models.Model):
    name = models.CharField(max_length=250)

    class Meta:
        verbose_name='documentType'
    def __str__(self):
        return self.name
    
class Document (models.Model):
    created = models.DateTimeField(default=timezone.now, null=True)
    name = models.ForeignKey(DocumentType, on_delete=models.DO_NOTHING, null=True)
    sum = models.IntegerField(default=0)

    class Meta:
        verbose_name='Documents'
    def __str__(self):
        return self.name

class RemainderHistory(models.Model):
    #temporary utility field for numbering rhos while displaying them at change_sale_posted html page
    number = models.IntegerField(default=0, null=True)#service field for enumerating selected rhos in arrays
    #number = models.IntegerField(default=0, required=False, read_only=True)#just an example
    created = models.DateTimeField(default=timezone.now, null=True)
    document = models.ForeignKey(Document, on_delete=models.DO_NOTHING, null=True, blank=True)
    #created = models.DateTimeField(format='%Y-%m-%dT%H:%M:%S', default=timezone.now, null=True)
    #created = serializers.DateTimeField(format='iso-8601', required=False, read_only=True)
    rho_type = models.ForeignKey(DocumentType, on_delete=models.DO_NOTHING, null=True)
    ean = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=250)
    status = models.CharField(max_length=50, null=True, blank=True)#displays who initiated the creation of rho (ozon, WB or myself)
    shipment_id = models.CharField(max_length=50, null=True, blank=True)
    ozon_sku = models.CharField(max_length=50, null=True, blank=True)
    ozon_id = models.CharField(max_length=50, null=True, blank=True)
    wb_id = models.CharField(max_length=50, null=True, blank=True)
    wb_bar_code = models.CharField(max_length=50, null=True, blank=True)
    article = models.CharField(max_length=50, null=True, blank=True)
    bar_code = models.CharField(max_length=50, null=True, blank=True)
    total_retail_sum = models.IntegerField(default=0)
    wholesale_price = models.IntegerField(default=0, null=True)
    av_price = models.IntegerField(default=0, null=True)
    retail_price = models.IntegerField(default=0)
    pre_remainder = models.IntegerField(default=0)
    incoming_quantity = models.IntegerField(null=True)
    outgoing_quantity = models.IntegerField(null=True)
    current_remainder = models.BigIntegerField(default=0)
    update_check = models.BooleanField(default=False)
    
    class Meta:
        ordering = ('-created',)  # sorting by date

class Identifier(models.Model):
    created = models.DateTimeField(default=timezone.now, null=True)
   
    def __int__(self):
        return self.id
    class Meta:
        ordering = ('-created',)  # sorting by date
  
class Report(models.Model):
    identifier = models.ForeignKey(Identifier, on_delete=models.DO_NOTHING, null=True, blank=True)
    #temporary utility field for numbering rhos while displaying them at change_sale_posted html page
    number = models.IntegerField(default=0, null=True)#service field for enumerating selected rhos in arrays
    #number = models.IntegerField(default=0, required=False, read_only=True)#just an example
    created = models.DateTimeField(default=timezone.now, null=True)
    #created = models.DateTimeField(format='%Y-%m-%dT%H:%M:%S', default=timezone.now, null=True)
    #created = serializers.DateTimeField(format='iso-8601', required=False, read_only=True)
    name = models.CharField(max_length=250)
    ozon_id = models.CharField(max_length=50, null=True, blank=True)
    article = models.CharField(max_length=50, null=True, blank=True)
    bar_code = models.CharField(max_length=50, null=True, blank=True)
    #total_retail_sum = models.IntegerField(default=0)
    #wholesale_price = models.IntegerField(default=0, null=True)
    #retail_price = models.IntegerField(default=0)
    pre_remainder = models.IntegerField(default=0)
    incoming_quantity = models.IntegerField(null=True)
    outgoing_quantity = models.IntegerField(null=True)
    current_remainder = models.IntegerField(default=0)
    av_price= models.IntegerField(default=0)
  
    class Meta:
        ordering = ('-created',)  # sorting by date

