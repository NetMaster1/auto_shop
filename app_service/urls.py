from django.urls import path
from . import views


urlpatterns = [
    path('db_correct', views.db_correct, name='db_correct'),
    path('product_quant_correct', views.product_quant_correct, name='product_quant_correct'),
    path('change_ozon_qnt_for_short_deflectors', views.change_ozon_qnt_for_short_deflectors, name='change_ozon_qnt_for_short_deflectors'),
    path('create_list_of_files', views.create_list_of_files, name='create_list_of_files'),
    path('rename_files', views.rename_files, name='rename_files'),
    path('db_correct_model_names', views.db_correct_model_names, name='db_correct_model_names'),
   
]