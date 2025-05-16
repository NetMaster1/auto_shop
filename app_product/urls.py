from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create_product', views.create_product, name='create_product'),
    path('getting_ozon_id', views.getting_ozon_id, name='getting_ozon_id'),

    path('delivery_auto', views.delivery_auto, name='delivery_auto'),
    path('synchronize_qnty', views.synchronize_qnty, name='synchronize_qnty'),
    path('sale', views.sale, name='sale'),
    path('update_prices', views.update_prices, name='update_prices'),
    path('update_images', views.update_images, name='update_images'),
    path('return_product', views.return_product, name='return_product'),
    path('general_report', views.general_report, name='general_report'),
    # path('choice', views.choice, name='choice'),
    # path('orders_history', views.orders_history, name='orders_history'),
]
