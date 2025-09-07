
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth import update_session_auth_hash, authenticate
from app_product.models import Product

def shopfront(request):
    products=Product.objects.all().order_by('name')
    context = {
        'products': products,
    }
    return render(request, 'shopfront.html', context)
