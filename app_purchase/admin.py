from django.contrib import admin
from app_product.models import Product
from . models import Cart, CartItem, Customer, Order

class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart_id', )
  
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'cart','quantity',)

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'f_name', 'l_name','email',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'status',)


admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Order, OrderAdmin)

