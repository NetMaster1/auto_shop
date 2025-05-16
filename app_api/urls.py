from django.urls import path, include
from . import views
from rest_framework import routers

router=routers.DefaultRouter()
router.register('api', views.ServerResponseView)


urlpatterns = [
    path('', include(router.urls)),
    path('ozon_push', views.ozon_push, name='ozon_push'),
   
]