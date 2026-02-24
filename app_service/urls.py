from django.urls import path
from . import views


urlpatterns = [
    path('db_correct', views.db_correct, name='db_correct'),
    path('product_quant_correct', views.product_quant_correct, name='product_quant_correct'),
    path('change_ozon_qnt_for_short_deflectors', views.change_ozon_qnt_for_short_deflectors, name='change_ozon_qnt_for_short_deflectors'),
    path('create_list_of_files', views.create_list_of_files, name='create_list_of_files'),
    path('rename_files', views.rename_files, name='rename_files'),
    path('db_correct_model_names', views.db_correct_model_names, name='db_correct_model_names'),
    path('delete_cart_items', views.delete_cart_items, name='delete_cart_items'),
    path('delete_carts', views.delete_carts, name='delete_carts'),
    path('html_test', views.html_test, name='html_test'),
    path('fill_in_search_name_col', views.fill_in_search_name_col, name='fill_in_search_name_col'),
    path('upload_reviews_from_ozon', views.upload_reviews_from_ozon, name='upload_reviews_from_ozon'),
    path('delete_reviews', views.delete_reviews, name='delete_reviews'),
    path('fill_in_product_percent_field', views.fill_in_product_percent_field, name='fill_in_product_percent_field'),
   
]