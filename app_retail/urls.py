from django.urls import path
from . import views


urlpatterns = [
    path('', views.shopfront, name='shopfront'),
 
]