from django.contrib import admin
from app_product.models import Product
from . models import Cart, CartItem, Customer, Order, OrderItem

class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart_id', 'cart_user', 'date_added' )
  
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'cart','quantity',)

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'f_name', 'l_name','email',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'status', 'delivery_order_uuid')
    
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product',)


admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)

