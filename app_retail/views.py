
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth import update_session_auth_hash, authenticate
from app_product.models import Product

def shopfront(request):
    products=Product.objects.filter(site_true=True).order_by('name')
    context = {
        'products': products,
    }
    return render(request, 'shopfront.html', context)

def search (request):
    if request.method == "POST":
        keyword = request.POST["brand"]
        keyword=keyword.upper()
        products=Product.objects.filter(name__contains=keyword, site_true=True).order_by('name')

        context = {
            'products': products,
        }

        return render(request, 'shopfront.html', context)
