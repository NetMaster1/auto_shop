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
    path('wb_limits', views.wb_limits, name='wb_limits'),
    path('wb_create_product', views.wb_create_product, name='wb_create_product'),
   
]