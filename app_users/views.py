from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth import update_session_auth_hash, authenticate

def login_page(request):
    return render(request, 'users/login_page.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            request.session.set_expiry(0)  #user session terminates on browser close
            #request.session.set_expiry(600) #user session terminates every 10 min
            auth.login(request, user)
            messages.success(request, 'You are logged in now')   
            return redirect("dashboard")
        else:
            messages.error(request, "Неправильные учетные данные, попробуйте еще раз")
            return redirect('login_page')
    else:
        return redirect('login_page')

def logout(request):
        auth.logout(request)
        # messages.success(request, 'Вы вышли из системы')
        return redirect('login')


