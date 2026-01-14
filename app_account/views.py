from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages, auth
from django.contrib.auth.models import User, Group
from app_product.models import Product
from app_purchase.models import Order, OrderItem
from . models import ExtendedUser
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
            else:
                if ExtendedUser.objects.filter(email=email).exists():
                    extended_user=ExtendedUser.objects.get(email=email)
                    extended_user.last_name=last_name
                    extended_user.first_name=first_name
                    extended_user.password=password
                    extended_user.save()
                else:
                    extended_user=ExtendedUser.objects.create(
                        password=password,
                        email=email, 
                        first_name=first_name, 
                        last_name=last_name,        
                        ) 
                security_code = []
                for i in range(4):
                    a = random.randint(0, 9)
                    security_code.append(a)
                    #transforming every integer into string
                    code_string = "".join(str(i) for i in security_code)  
                    #print(code_string)
                extended_user.email_confirm_code=code_string
                extended_user.save()
                
                send_mail(
                    'Подтверждение e-mail для auto-deflector.ru',
                    f"""Здравствуйте, вы получили данный код для подтверждения вашей эл. почты на сайте auto-deflector.ru.
                    Если вы не регистрировались на данном сайте, пожалуйста, удалите данное сообщение.
                    Код для подтверждения: {code_string}.
                    Введите его на сайте""",
                    'support@auto-deflector.ru',
                    [email,],
                    fail_silently=False
                )     
                return redirect ('email_confirmation', extended_user.id)         
        else:
            messages.error(request, "Пароли не совпадают. Попробуйте еще раз.")
            return redirect('shopfront')
        
def email_confirmation(request, extended_user_id):
    extended_user=ExtendedUser.objects.get(id=extended_user_id)
    context={
        'extended_user': extended_user
        }
    return render (request, 'accounts/email_confirmation_page.html', context)

def confirm_email(request, extended_user_id):
    extended_user=ExtendedUser.objects.get(id=extended_user_id)
    if request.method == 'POST':
        security_string = request.POST['security_string']
        if security_string == extended_user.email_confirm_code:
            user = User.objects.create_user(
                username=extended_user.email,
                password=extended_user.password,
                email=extended_user.email, 
                first_name=extended_user.first_name, 
                last_name=extended_user.last_name
                )
            extended_user.user=user
            extended_user.password=None
            extended_user.email_confirm=True
            extended_user.save()
    
            auth.login(request, user)
            # url=f'www.auto-deflector.ru/accountemail_cofirmation/{user.id}/{email}'
            messages.error(request, "Вы успешно создали учетную запись на auto-deflector.ru")
            return redirect ('account_page', user.id)
        else:
            # if security_string != extended_user.email_confirm_code:
            messages.error(request, "Неверный код подтверждения. Попробуйте еще раз.")
            return redirect ('email_confirmation', extended_user.id)
            


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
    
def change_password(request, user_id):
    pass



