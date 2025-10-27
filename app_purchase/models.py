from django.db import models
# import datetime
from datetime import datetime, date
from django.utils import timezone
from app_product.models import Product
# import pytz


class Identifier(models.Model):
    created = models.DateTimeField(default=timezone.now, null=True)
    def __int__(self):
        return self.id

class Customer (models.Model):
    f_name = models.CharField(max_length=50)
    l_name = models.CharField(max_length=50)
    phone=models.CharField(max_length=50)
    created = models.DateField(auto_now_add=True)#creation stamp
    
    def __int__(self):
        return self.id

class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    #date_added = models.DateField(auto_now_add=True)

    # class Meta:
    #     db_table = 'Cart'
    #     ordering = ['date_added']

    def __str__(self):
        return self.cart_id
    #def __unicode__(self):
    #    return "Cart id: %s" %(self.id)

class CartItem(models.Model):
    brand = models.CharField(max_length=100, blank=True)
    product = models.CharField(max_length=100)
    article = models.CharField(max_length=100,null=True, blank=True )
    image = models.ImageField(upload_to='uploads', blank=True)
    slug = models.SlugField(max_length=100, null=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'CartItem'

    def sub_total(self):
        return self.price * self.quantity
    

    def __str__(self):
        return self.product

class Order(models.Model):
    created = models.DateTimeField(default=timezone.now, null=True)
    sum = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    client = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.DO_NOTHING)
    paid=models.BooleanField(default=False)
    shipped=models.BooleanField(default=False)
    delivery_point = models.CharField(max_length=100, null=True, blank=True)
    receiver_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.product

class OrderItem(models.Model):
    order = models.ForeignKey(Order, null=True, on_delete=models.DO_NOTHING)
    product = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='uploads', blank=True)
    article = models.CharField(max_length=50,null=True, blank=True )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    sub_total = models.DecimalField(default=0, max_digits=7, decimal_places=2, null=True, blank=True)

    # def sub_total(self):
    #     return self.price * self.quantity

    def __str__(self):
        return self.product

class ProductPurchased (models.Model):
    created = models.DateTimeField(auto_now=True)
    #user_name = models.CharField(max_length=50, null =True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    def __int__(self):
        return self.id
