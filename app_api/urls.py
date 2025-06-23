from django.urls import path, include
from . import views
from rest_framework import routers

router=routers.DefaultRouter()
router.register('api', views.ServerResponseView)


urlpatterns = [
    path('', include(router.urls)),
    path('ozon_push', views.ozon_push, name='ozon_push'),
    path('wb_test', views.wb_test, name='wb_test'),
    path('wb_categories', views.wb_categories, name='wb_categories'),
    path('wb_subjects', views.wb_subjects, name='wb_subjects'),
    path('wb_subject_specs', views.wb_subject_specs, name='wb_subject_specs'),
    path('wb_colors', views.wb_colors, name='wb_colors'),
    path('wb_country_of_manufacture', views.wb_country_of_manufacture, name='wb_country_of_manufacture'),
    path('wb_limits', views.wb_limits, name='wb_limits'),
    path('wb_add_media_files', views.wb_add_media_files, name='wb_add_media_files'),
    path('wb_change_qnty', views.wb_change_qnty, name='wb_change_qnty'),
    path('wb_warehouse_list', views.wb_warehouse_list, name='wb_warehouse_list'),
    path('wb_create_warehouse', views.wb_create_warehouse, name='wb_create_warehouse'),
    path('wb_seller_warehouse_list', views.wb_seller_warehouse_list, name='wb_seller_warehouse_list'),
    path('wb_id', views.wb_id, name='wb_id'),
   
]