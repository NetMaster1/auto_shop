from django.shortcuts import render, redirect
from app_product.models import Product
from app_purchase.models import Order, OrderItem
from . models import ExtendedUser
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages, auth
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
import random
from django.http import HttpResponse
import secrets 
import string

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
                user=User.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    )
            if ExtendedUser.objects.filter(user=user).exists():
                pass
            else:
                extended_user=ExtendedUser.objects.create(
                    user=user,
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
            return redirect ('email_confirmation', user.id)         
        else:
            messages.error(request, "Пароли не совпадают. Попробуйте еще раз.")
            return redirect('shopfront')
        
def email_confirmation(request, user_id):
    user=User.objects.get(id=user_id)
    context={
        'user': user,
        }
    return render (request, 'accounts/email_confirmation_page.html', context)

def confirm_email(request, user_id):
    user=User.objects.get(id=user_id)
    extended_user=ExtendedUser.objects.get(user=user)
    if request.method == 'POST':
        security_string = request.POST['security_string']
        if security_string == extended_user.email_confirm_code:
            if ExtendedUser.objects.filter(user=user).exists():
                extended_user=ExtendedUser.objects.get(user=user)
                extended_user.email_confirm=True
                extended_user.save()
                auth.login(request, user)           
                # url=f'www.auto-deflector.ru/accountemail_cofirmation/{user.id}/{email}'
                messages.error(request, "Вы успешно создали учетную запись на auto-deflector.ru")
                return redirect ('account_page', user.id)
            else:
                messages.error(request, "Произошла ошибка. Попробуйте зарегистрироваться еще раз")
                return redirect ('email_confirmation', user.id)
                
        else:
            # if security_string != extended_user.email_confirm_code:
            messages.error(request, "Неверный код подтверждения. Попробуйте еще раз.")
            return redirect ('email_confirmation', user.id)
            
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
        extended_user=ExtendedUser.objects.get(user=user)
        orders=Order.objects.filter(user=user, status='succeeded')

        if request.user.id == user.id:
            context={
                'user': user,
                'orders': orders,
                'extended_user': extended_user,
                # 'orders_dict': orders_dict
            }
            return render(request, 'accounts/account_page.html', context)
    else:
        return redirect ('shopfront')

def change_password(request, user_id):
    if request.user.is_authenticated:
        user=User.objects.get(id=user_id)
        username=user.username
        if request.method == 'POST':
            password = request.POST['password']
            check_password = request.POST['check_password']
            code = request.POST['code']
            if password == check_password:
                extended_user=ExtendedUser.objects.get(user=user)
                if code == extended_user.email_confirm_code:
                    user.set_password(password)
                    #user.password=password
                    user.save()
                    user = authenticate(request, username=username, password=password)
                    login(request, user)
                    return redirect ('account_page', user.id)
                else:
                    messages.error(request, "Неправильный код из письма. Попробуйте еще раз.")
                    return redirect ('account_page', user.id)
            else:
                messages.error(request, "Пароли не совпадают. Попробуйте еще раз. ")
                return redirect ('password_change_page', user.id)
    else:
        return redirect ('shopfront')

def send_random_code(request, user_id):
    if request.user.is_authenticated:
        user=User.objects.get(id=user_id)
        security_code = []
        for i in range(4):
            a = random.randint(0, 9)
            security_code.append(a)
            #transforming every integer into string
            code_string = "".join(str(i) for i in security_code)  
            #print(code_string)
        extended_user=ExtendedUser.objects.get(user=user)
        extended_user.email_confirm_code=code_string
        extended_user.save()
        send_mail(
            'Проверочный код для изменения пароля',
            f"""Здравствуйте, вы получили данный код для подтверждения изменения пароля на сайте auto-deflector.ru.
            Если вы не пытались изменить пароль на данном сайте, пожалуйста, удалите данное сообщение.
            Код для подтверждения: {code_string}.
            Введите его на сайте""",
            'support@auto-deflector.ru',
            [user.email,],
            fail_silently=False
            )
        return redirect ('password_change_page', user.id)
    else:
        return redirect ('shopfront')
    
def password_change_page(request, user_id):
    if request.user.is_authenticated:
        user=User.objects.get(id=user_id)
        context={
            'user': user
            }
        return render(request, 'accounts/password_change_page.html', context)
    else:
        return redirect ('shopfront')

def password_recovery_page(request):
    return render(request, 'accounts/password_recovery_page.html')

def recover_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        print(email)
        if User.objects.filter(email=email).exists():
            user=User.objects.get(email=email)
            print('True')
            #characters = string.ascii_letters + string.digits + string.punctuation
            characters = string.ascii_letters + string.digits
            #password = "".join(secrets.choice(characters) for i in range(8))
            password = "".join(random.choice(characters) for i in range(8))
            
            send_mail(
                'Новый пароль',
                f"""Здравствуйте, пароль был изменен.
                Если вы не пытались изменить пароль на данном сайте, пожалуйста, удалите данное сообщение.
                Новый пароль: {password}
                Войдите с новым паролем""",
                'support@auto-deflector.ru',
                [user.email,],
                fail_silently=False
                )
            username=user.username
            user.set_password(password)
            user.save()
            user = authenticate(request, username=username, password=password)

            messages.error(request, "Пароль был изменён. Войдите с новым паролем.")
            return redirect ('shopfront')
                

        else:
            messages.error(request, "База данных не содержит данного почтового ящика.")
            return redirect ('password_recovery_page')

def create_sdek_phone(request, user_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            phone = request.POST['phone']
            user=User.objects.get(id=user_id)
            extended_user=ExtendedUser.objects.get(user=user)
            extended_user.sdek_phone=phone
            extended_user.save()
            return redirect ('account_page', user.id)
    else:
        auth.logout(request)
        return redirect ('shopfront')
    

def create_ozon_phone(request, user_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            phone = request.POST['phone']
            user=User.objects.get(id=user_id)
            extended_user=ExtendedUser.objects.get(user=user)
            extended_user.ozon_phone=phone
            extended_user.save()
            return redirect ('account_page', user.id)
    else:
        auth.logout(request)
        return redirect ('shopfront')