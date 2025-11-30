"""
URL configuration for shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include ('app_retail.urls')),
    path('users', include ('app_users.urls')),
    path('product', include ('app_product.urls')),
    path('report', include ('app_report.urls')),
    path('service', include ('app_service.urls')),
    path('api', include ('app_api.urls')),
    path('purchase', include ('app_purchase.urls')),
    path('reviews', include ('app_reviews.urls')),
    path('reference', include ('app_reference.urls')),
    path('delivery', include ('app_delivery.urls')),
    path('account', include ('app_account.urls')),
   
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
