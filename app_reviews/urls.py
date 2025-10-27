from django.urls import path
from . import views


urlpatterns = [
    path('rating/<int:product_id>/', views.rating, name='rating'),
    path('review', views.review, name='review'),
    
]