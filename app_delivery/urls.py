from django.urls import path
from . import views


urlpatterns = [
    path('get_list_of_sdek_offices', views.get_list_of_sdek_offices, name='get_list_of_sdek_offices'),
    path('get_list_of_sdek_cities', views.get_list_of_sdek_cities, name='get_list_of_sdek_cities'),
    path('get_list_of_sdek_locations', views.get_list_of_sdek_locations, name='get_list_of_sdek_locations'),
    path('get_sdek_delivery_cost', views.get_sdek_delivery_cost, name='get_sdek_delivery_cost'),

    path('sdek_country_choice/<int:order_id>', views.sdek_country_choice, name='sdek_country_choice'),
    
    path('open_sdek_vidget', views.open_sdek_vidget, name='open_sdek_vidget'),
 
]