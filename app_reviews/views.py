from django.shortcuts import render, redirect
from app_product.models import Product
from . models import Rating

def rating(request, product_id):
    # if request.user.is_authenticated:
    if 'rating' in request.GET:
        rating_given = request.GET['rating']
        rating_given = int(rating_given)
        product=Product.objects.get(article=product_id)
        
        counter = product.total + rating_given
        product.total=counter
        counter_1 = product.quantity + 1
        product.quantity=counter_1
        product.av_rating = product.total / product.quantity

        var = str(product.av_rating / 5 * 100)
        percent = '%'
        product.percent=var+percent
        product.save()

        rating = Rating.objects.create(
            #user=request.user,
            product=product,
            rating=rating_given
        )
    return redirect('shopfront' )
           
    # return redirect('login')

def review (request):
    product=Product.objects.get(id=150)
    context = {
        'product' : product
    }
    return render (request, 'review.html', context)