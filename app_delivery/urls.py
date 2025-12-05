from django.urls import path
from . import views


urlpatterns = [
    path('get_list_of_sdek_offices', views.get_list_of_sdek_offices, name='get_list_of_sdek_offices'),
    path('get_list_of_sdek_cities', views.get_list_of_sdek_cities, name='get_list_of_sdek_cities'),
    path('get_list_of_sdek_locations', views.get_list_of_sdek_locations, name='get_list_of_sdek_locations'),
    path('get_sdek_delivery_cost', views.get_sdek_delivery_cost, name='get_sdek_delivery_cost'),
    path('get_list_of_sdek_tariffs', views.get_list_of_sdek_tariffs, name='get_list_of_sdek_tariffs'),
    path('get_order_status', views.get_order_status, name='get_order_status'),
    path('open_sdek_vidget', views.open_sdek_vidget, name='open_sdek_vidget'),
    path('sdek_office_choice/<int:order_id>/', views.sdek_office_choice, name='sdek_office_choice'),
    path('sdek_shipment_order/<int:order_id>/', views.sdek_shipment_order, name='sdek_shipment_order'),
    
 
]