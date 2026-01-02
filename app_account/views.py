from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages, auth
from django.contrib.auth.models import User, Group
from app_product.models import Product
from app_purchase.models import Order, OrderItem
from django.core.mail import send_mail
import random

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
                
                # security_code = []
                # for i in range(4):
                #     a = random.randint(0, 9)
                #     security_code.append(a)
                #     #transforming every integer into string
                #     code_string = "".join(str(i) for i in security_code)  
                #     #print(code_string)
                
                # send_mail(
                #     'Подтверждение e-mail для auto-deflector.ru',
                #     f"""Здравствуйте, вы получили данный код для подтверждения вашей эл. почты на сайте auto-deflector.ru.
                #     Если вы не регистрировались на данном сайте, пожалуйста, удалите данное сообщение.
                #     Код для подтверждения: {code_string}""",
                #     'support@auto-deflector.ru',
                #     ['Sergei_Vinokurov@rambler.ru',],
                #     fail_silently=False
                # )
                    
                messages.error(request, "Вам необходимо подтвердить свою электронную почту. Нажмите email > подтвердить > введите код полученный в письме.")
                return redirect ('account_page', user.id)

        else:
            messages.error(request, "Пароли не совпадают. Попробуйте еще раз.")
            return redirect('register_user')

def email_confirm(request):
    pass

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            #messages.success(request, ('Your have successfully been logged in. Welcome to ruversity.com'))
            messages.success(request, ('Добро пожаловать. Вы успешно вошли в свой профиль.'))
            return redirect('shopfront')
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
    if request.user.is_authenticated:
        user=User.objects.get(id=user_id)
        orders=Order.objects.filter(user=user, status='succeeded')
        # orders_dict={}
        # for order in orders:
        #     order_items=OrderItem.objects.filter(order=order)
        #     for order_item in order_items:
        #         order_items_arr=[]
        #         product=order_item.product
        #         order_items_arr.append(product)
        #     orders_dict[order]=order_items_arr

        if request.user.id == user.id:
            context={
                'user': user,
                'orders': orders,
                # 'orders_dict': orders_dict
            }
            return render(request, 'accounts/account_page.html', context)
    else:
        return redirect ('shopfront')



