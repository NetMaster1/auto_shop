from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create_product', views.create_product, name='create_product'),
    path('product_page/<str:article>', views.product_page, name='product_page'),

    path('getting_ozon_id_and_ozon_sku', views.getting_ozon_id_and_ozon_sku, name='getting_ozon_id_and_ozon_sku'),

    path('delivery_auto', views.delivery_auto, name='delivery_auto'),
    path('zero_ozon_qnty', views.zero_ozon_qnty, name='zero_ozon_qnty'),
    path('synchronize_qnty', views.synchronize_qnty, name='synchronize_qnty'),
    path('synchronize_qnty_wb_ver_1', views.synchronize_qnty_wb_ver_1, name='synchronize_qnty_wb_ver_1'),
    path('synchronize_qnty_wb_warehouse', views.synchronize_qnty_wb_warehouse, name='synchronize_qnty_wb_warehouse'),
    path('synchronize_qnty_SDEK_warehouse', views.synchronize_qnty_SDEK_warehouse, name='synchronize_qnty_SDEK_warehouse'),
    path('sale', views.sale, name='sale'),
    path('recognition', views.recognition, name='recognition'),
    path('update_prices', views.update_prices, name='update_prices'),
    path('update_images', views.update_images, name='update_images'),
    path('return_product', views.return_product, name='return_product'),
    path('general_report', views.general_report, name='general_report'),
    # path('choice', views.choice, name='choice'),
    # path('orders_history', views.orders_history, name='orders_history'),

    path('wb_create_product', views.wb_create_product, name='wb_create_product'),
    path('wb_add_media_files', views.wb_add_media_files, name='wb_add_media_files'),
    path('wb_get_id', views.wb_get_id, name='wb_get_id'),
    path('wb_update_prices', views.wb_update_prices, name='wb_update_prices'),
    path('wb_update_prices_ver_1', views.wb_update_prices_ver_1, name='wb_update_prices_ver_1'),
    path('zero_wb_qnty', views.zero_wb_qnty, name='zero_wb_qnty'),
    path('wb_ozon_sync', views.wb_ozon_sync, name='wb_ozon_sync'),

    path('change_site_retail_price', views.change_site_retail_price, name='change_site_retail_price'),
]
