from django.shortcuts import render, redirect
from app_product.models import Product
from . models import Review
from django.contrib.auth.models import User

# def rating(request, product_id):
#     # if request.user.is_authenticated:
#     if 'rating' in request.GET:
#         rating_given = request.GET['rating']
#         rating_given = int(rating_given)
#         product=Product.objects.get(article=product_id)
        
#         counter = product.total + rating_given
#         product.total=counter
#         counter_1 = product.quantity + 1
#         product.quantity=counter_1
#         product.av_rating = product.total / product.quantity

#         var = str(product.av_rating / 5 * 100)
#         percent = '%'
#         product.percent=var+percent
#         product.save()

#         rating = Rating.objects.create(
#             #user=request.user,
#             product=product,
#             rating=rating_given
#         )
#     return redirect('shopfront' )
           
    # return redirect('login')

def create_product_review (request, user_id):
    if request.user.is_authenticated:
        user=User.objects.get(id=user_id)
        if request.method == 'POST':
            article=request.POST['article']
            review=request.POST['review']
            rating=request.POST['rating']
            product=Product.objects.get(article=article)
            review=Review.objects.create (
                author=user,
                product=product,
                content=review,
                rating=rating
                )
            review.caclulate_percent()
            review.save()
            reviews=Review.objects.filter(product=product) 
            number_of_reviews=len(reviews)
            print(f'Number of reviews:  {number_of_reviews}')
            total_rating=0
            
            for review in reviews:
                total_rating+=review.rating
            print(f'Total rating:   {total_rating}')
            average_rating=total_rating/number_of_reviews
            product.av_rating=average_rating
            product.caclulate_percent()
            product.save()
            print(product.av_rating)
            return redirect ('account_page', user.id)
            



