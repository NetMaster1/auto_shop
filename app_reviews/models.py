from django.db import models
from app_product.models import Product
from django.contrib.auth.models import User
from django.utils import timezone


class Review (models.Model):
    content = models.TextField(null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    #date_posted = models.DateField(auto_now_add=True)
    date_posted = models.DateTimeField(default=timezone.now, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(blank=True, null=True)
    percent = models.CharField(max_length=50, default='0%')#we need this column to display the rating of each review in stars
    ozon_id = models.CharField(max_length=100, null=True, blank=True)

    def caclulate_percent(self):
        percent= int(self.rating) / 5 * 100
        percent = f'{percent}'
        self.percent= percent + '%'

    def __int__(self):
        return self.id
    

    

