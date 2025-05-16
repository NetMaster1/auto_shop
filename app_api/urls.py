from django.urls import path, include
from . import views
from rest_framework import routers

router=routers.DefaultRouter()
router.register('api', views.ServerResponseView)


urlpatterns = [
    path('', include(router.urls)),
    path('receive_ozon_push_message', views.receive_ozon_push_message, name='receive_ozon_push_message'),
   
]