from django.urls import path
from . import views


urlpatterns = [
    path('email_auth', views.email_auth, name='email_auth'),
   
]
