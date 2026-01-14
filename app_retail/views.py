
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth import update_session_auth_hash, authenticate
from app_product.models import Product
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

def shopfront(request):
    #products=Product.objects.filter(site_true=True, image_1__isnull=False).order_by('name')
    products=Product.objects.filter(site_true=True, image_1__contains='png').order_by('name')
    #products=Product.objects.filter(site_true=True).order_by('name')
    print(products.count())
    #============paginator module=================
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    #=============end of paginator module===============
    context = {
        'queryset_list': paged_products,
        'products': products
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
