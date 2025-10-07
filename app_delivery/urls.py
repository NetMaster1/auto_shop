from django.urls import path
from . import views


urlpatterns = [
    path('get_list_of_sdek_offices', views.get_list_of_sdek_offices, name='get_list_of_sdek_offices'),
 
]