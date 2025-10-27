from django.db import models
from app_product.models import Product

# Create your models here.
class Transaction(models.Model):
    date_created = models.DateField(auto_now_add=True)
    money_paid = models.BooleanField(default=False)#check if money have been paid
    payment_id = models.CharField(max_length=100, null=True)
    # course = models.ForeignKey(MainSubject, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    # date_paid = models.DateField(null=True)
    paid_amount = models.FloatField(null=True)
  
    def __int__(self):
        return self.id