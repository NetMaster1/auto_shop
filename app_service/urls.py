from django.urls import path
from . import views


urlpatterns = [
    path('', views.db_correct, name='db_correct'),
    path('product_quant_correct', views.product_quant_correct, name='product_quant_correct'),
   
]