from django.urls import path
from . import views


urlpatterns = [
    path('get_list_of_sdek_offices', views.get_list_of_sdek_offices, name='get_list_of_sdek_offices'),
    path('get_list_of_sdek_cities', views.get_list_of_sdek_cities, name='get_list_of_sdek_cities'),
    path('get_list_of_sdek_locations', views.get_list_of_sdek_locations, name='get_list_of_sdek_locations'),
    path('get_sdek_delivery_cost', views.get_sdek_delivery_cost, name='get_sdek_delivery_cost'),
    path('get_list_of_sdek_tarifs', views.get_list_of_sdek_tarifs, name='get_list_of_sdek_tarifs'),
    path('sdek_office_choice/<int:order_id>/', views.sdek_office_choice, name='sdek_office_choice'),
    path('sdek_shipment_address/<int:order_id>/', views.sdek_shipment_address, name='sdek_shipment_address'),
    path('create_sdek_delivery_order/<int:order_id>', views.create_sdek_delivery_order, name='create_sdek_delivery_order'),
    
    path('open_sdek_vidget', views.open_sdek_vidget, name='open_sdek_vidget'),
 
]