from django.urls import path
from . import views


urlpatterns = [
    path('load_auto_brands', views.load_auto_brands, name='load_auto_brands'),
   
]