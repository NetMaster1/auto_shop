from django.db import models
from datetime import datetime, date
from django.utils import timezone
from django.contrib.auth.models import User
#from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# Create your models here.
class ExtendedUser (models.Model):
    # first_name = models.CharField(max_length=50, null=True, blank=True)
    # last_name = models.CharField(max_length=50, null=True, blank=True)
    # password = models.CharField(max_length=50, null=True, blank=True)
    user=models.ForeignKey(User,on_delete=models.DO_NOTHING, null=True, blank=True)
    # email=models.EmailField(max_length=100, blank=True, null=True)
    email_confirm = models.BooleanField(default=False)
    email_confirm_code = models.CharField(max_length=50, null=True, blank=True)
    sdek_phone = models.CharField(max_length=50, null=True, blank=True)
    sdek_phone_confirm = models.BooleanField(default=False)
    ozon_phone=models.CharField(max_length=50, null=True, blank=True)
    ozon_phone_confirm = models.BooleanField(default=False)
    phone_confirm_code=models.CharField(max_length=50, null=True, blank=True)
    
    def __int__(self):
        return self.id


# class CustomAccountManager(BaseUserManager):
    
#     def create_superuser(self, first_name, email, user_name, password, **other_fields):
#         other_fields.setdefault('is_staff', True)
#         other_fields.setdefault('is_superuser', True)
#         other_fields.setdefault('is_active', True)
    
#     def create_user(self, email, user_name, first_name, last_name, phone, password, **other_fields):
#         email = self.normalize_email(email)
#         user=self.model(email=email, user_name=user_name, first_name=first_name, **other_fields)
#         user.set_password(password)
#         user.save()
        
#         return user


# class NewUser (AbstractBaseUser, PermissionsMixin):
#     first_name = models.CharField(max_length=50, blank=True)
#     last_name = models.CharField(max_length=50, blank=True)
#     phone=models.CharField(max_length=50)
#     email=models.EmailField(max_length=100, unique=True)
#     user_name=models.CharField(max_length=100, unique=True)
#     created = models.DateField(auto_now_add=True)#creation stamp
#     is_staff = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=False)
#     email_confirm = models.BooleanField(default=False)
#     phone_confirm = models.BooleanField(default=False)
    
#     objects = CustomAccountManager()
    
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS=['user_name', 'first_name']
    
#     def __str__(self):
#         return self.user_name