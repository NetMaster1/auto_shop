from django.urls import path
from . import views


urlpatterns = [
    path('register_user', views.register_user, name='register_user'),
    path('login_user', views.login_user, name='login_user'),
    path('logout_user', views.logout_user, name='logout_user'),
    path('account_page/<int:user_id>', views.account_page, name='account_page'),
    path('confirm_email/<int:user_id>', views.confirm_email, name='confirm_email'),
    path('email_cofirmation/<int:user_id>', views.email_confirmation, name='email_confirmation'),
    path('chage_password/<int:user_id>', views.change_password, name='change_password'),
    path('send_random_code/<int:user_id>', views.send_random_code, name='send_random_code'),
    path('pass_change_page/<int:user_id>', views.pass_change_page, name='pass_change_page'),
  
 
]