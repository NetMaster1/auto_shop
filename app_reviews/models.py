from django.db import models
from app_product.models import Product

class Review (models.Model):
    content = models.TextField(null=True, blank=True)
    #author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_posted = models.DateField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __int__(self):
        return self.id
    

