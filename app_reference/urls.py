from django.urls import path
from . import views


urlpatterns = [
    path('load_auto_brands', views.load_auto_brands, name='load_auto_brands'),
    path('load_auto_models', views.load_auto_models, name='load_auto_models'),
    path('load_auto_modifications', views.load_auto_modifications, name='load_auto_modifications'),
   
]