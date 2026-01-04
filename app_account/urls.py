from django.urls import path
from . import views


urlpatterns = [
    path('register_user', views.register_user, name='register_user'),
    path('login_user', views.login_user, name='login_user'),
    path('logout_user', views.logout_user, name='logout_user'),
    path('account_page/<int:user_id>', views.account_page, name='account_page'),
    path('confirm_email/<int:extended_user_id>', views.confirm_email, name='confirm_email'),
    path('email_cofirmation/<int:extended_user_id>', views.email_confirmation, name='email_confirmation'),
  
 
]