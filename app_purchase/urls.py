from django.urls import path
from . import views


urlpatterns = [
    # path('<str:article>', views.credit_card, name='credit_card'),
    path('cart_detail', views.cart_detail, name='cart_detail'),
    #path('add_cart/<str:article>', views.add_cart, name='add_cart'),
    path('add_cart/<int:id>', views.add_cart, name='add_cart'),
    path('remove_cart_item/<int:id>', views.remove_cart_item, name='remove_cart_item'),
    path('add_cart_item/<int:id>', views.add_cart_item, name='add_cart_item'),
    path('delete_cart_item/<int:id>', views.delete_cart_item, name='delete_cart_item'),
    path('purchase_product', views.purchase_product, name='purchase_product'),
    path('order/<int:order_id>', views.order, name='order'),
    path('order_including_sdek_shipment/<int:order_id>/', views.order_including_sdek_shipment, name='order_including_sdek_shipment'),
    path('make_payment/<int:order_id>', views.make_payment, name='make_payment'), 
    #path('create_sdek_delivery_order/<int:order_id>', views.create_sdek_delivery_order, name='create_sdek_delivery_order'),
   
]