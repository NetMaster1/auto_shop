from django.shortcuts import render, redirect
from app_product.models import Product, RemainderHistory
import pandas
import xlwt
from django.contrib import messages

def db_correct(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            file = request.FILES["file_name"]
            df1 = pandas.read_excel(file)
            cycle = len(df1)
            for i in range(cycle):
                row = df1.iloc[i]#reads each row of the df1 one by one
                article=row.Article
                if Product.objects.filter(article=article).exists():
                    product=Product.objects.get(article=article)
                    product.name=row.Title
                    product.save()
                if RemainderHistory.objects.filter(article=article).exists():
                    rhos=RemainderHistory.objects.filter(article=article)
                    for rho in rhos:
                        rho.name=row.Title
                        rho.save()
            return redirect('dashboard')

    return redirect ('login_page')

def product_quant_correct(request):
    if request.user.is_authenticated:
        products=Product.objects.all()
        for product in products:
            if RemainderHistory.objects.filter(article=product.article).exists():
                rho_latest = RemainderHistory.objects.filter(article=product.article).latest('created')
                product.quantity=rho_latest.current_remainder
                product.total_sum=rho_latest.current_remainder*product.av_price
                product.save()
        messages.success(request, 'Product table quantity and total_sum changed')   
        return redirect("dashboard")   
        return redirect('dashboard')
            


