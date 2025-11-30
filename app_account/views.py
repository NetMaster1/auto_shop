from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages, auth
from django.contrib.auth.models import User, Group

# Create your views here.
def register_user(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        # email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            # Check user name
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Пользователь с таким логином уже существует.')
                return redirect('register_user')
            # else:
            #     if User.objects.filter(email=email).exists():
            #         messages.error(request, 'Такой адрес электронной почты уже существует.')
            #         return redirect('register_user')
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    # email=email, 
                    email=username, 
                    first_name=first_name, 
                    last_name=last_name)

                # saving the request.user
                user.save()
                auth.login(request, user)


        else:
            messages.error(request, "Пароли не совпадают. Попробуйте еще раз.")
            return redirect('register_user')
        
        context={
            'user':user,
        }

    else:
        return render(request, 'accounts/account_page.html', context)
    



def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            #messages.success(request, ('Your have successfully been logged in. Welcome to ruversity.com'))
            messages.success(request, ('Вы успешно вошли. Добро пожаловать на ruversity.com'))
            return redirect('main_page')
        else:
            #messages.error(request, ('Incorrect username or password. Check your credentials & try again'))
            messages.error(request, ('Неправильное имя пользователи или пароль. Проверьте ваше данные и попробуйте еще раз'))
            return redirect('login')
    else:
        return render(request, 'accounts/login.html')


def logout_user(request):
    logout(request)
    #messages.success(request, ('You are now logged out'))
    messages.success(request, ('Вы вышли из личного кабинета ruversity.com'))
    return redirect('index')


# def dashboard(request):
#     if request.user.is_authenticated:
#         return render(request, 'accounts/dashboard.html')
#     else:
#         return redirect('login')
