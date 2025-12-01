from django.shortcuts import render, redirect
from django.core.mail import send_mail
#from shop.settings import EMAIL_HOST_USER
import smtplib


# Create your views here.
def email_auth(request):
    send_mail(
        'Hello from DjangoDev',
        'Here goes email text',
        'support@auto-deflector.ru',
        ['Sergei_Vinokurov@rambler.ru',],
        fail_silently=False
    )
    return redirect('shopfront')

