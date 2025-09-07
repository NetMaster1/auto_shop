from django.contrib import admin
from app_product.models import Product
from . models import Cart, CartItem

class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart_id', )
  
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'cart','quantity',)



admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)

