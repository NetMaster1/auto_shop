from django.urls import path
from . import views


urlpatterns = [
    path('create_product_review/<int:user_id>/', views.create_product_review, name='create_product_review'),
    
]