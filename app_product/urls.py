from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create_product', views.create_product, name='create_product'),
    path('getting_ozon_id_and_ozon_sku', views.getting_ozon_id_and_ozon_sku, name='getting_ozon_id_and_ozon_sku'),

    path('delivery_auto', views.delivery_auto, name='delivery_auto'),
    path('zero_ozon_qnty', views.zero_ozon_qnty, name='zero_ozon_qnty'),
    path('synchronize_qnty', views.synchronize_qnty, name='synchronize_qnty'),
    path('sale', views.sale, name='sale'),
    path('update_prices', views.update_prices, name='update_prices'),
    path('update_images', views.update_images, name='update_images'),
    path('return_product', views.return_product, name='return_product'),
    path('general_report', views.general_report, name='general_report'),
    # path('choice', views.choice, name='choice'),
    # path('orders_history', views.orders_history, name='orders_history'),

    path('wb_create_product', views.wb_create_product, name='wb_create_product'),
    path('wb_add_media_files', views.wb_add_media_files, name='wb_add_media_files'),
    path('wb_get_id', views.wb_get_id, name='wb_get_id'),
]
