from django.urls import path
from . import views


urlpatterns = [
    path('', views.db_correct, name='db_correct'),
    path('product_quant_corrent', views.product_quant_corrent, name='product_quant_corrent'),
   
]