from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages, auth
from django.contrib.auth.models import User, Group
from app_product.models import Product
from app_purchase.models import Order, OrderItem

# Create your views here.
def register_user(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['email']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            # Check user name
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Пользователь с таким логином уже существует.')
                return redirect('shopfront')
            # else:
            #     if User.objects.filter(email=email).exists():
            #         messages.error(request, 'Такой адрес электронной почты уже существует.')
            #         return redirect('register_user')
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email, 
                    first_name=first_name, 
                    last_name=last_name)

                # saving the request.user
                user.save()
                auth.login(request, user)
                return redirect ('account_page', user.id)

        else:
            messages.error(request, "Пароли не совпадают. Попробуйте еще раз.")
            return redirect('register_user')
   

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            #messages.success(request, ('Your have successfully been logged in. Welcome to ruversity.com'))
            messages.success(request, ('Вы успешно вошли. Добро пожаловать на вашу личную страницу.'))
            return redirect('account_page', user.id)
        else:
            #messages.error(request, ('Incorrect username or password. Check your credentials & try again'))
            messages.error(request, ('Неправильное имя пользователи или пароль. Проверьте ваше данные и попробуйте еще раз'))
            return redirect('shopfront')


def logout_user(request):
    auth.logout(request)
    #messages.success(request, ('You are now logged out'))
    messages.success(request, ('Вы вышли из личного кабинета'))
    return redirect('shopfront')

def account_page(request, user_id ):
    user=User.objects.get(id=user_id)
    orders=Order.objects.filter(user=user)
    # for order in orders:
    #     if order.paid==True:
    #         order_items=OrderItem.objects.filter(order=order)
    #         for order_item in order_items:
    #             product=order_item.product
    #             order_item.product=product

    if request.user.is_authenticated:
        if request.user.id == user.id:
            context={
                'user': user,
                'orders': orders,
            }
        return render(request, 'accounts/account_page.html', context)



