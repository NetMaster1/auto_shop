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
    path('password_change_page/<int:user_id>', views.password_change_page, name='password_change_page'),
    path('password_recovery_page', views.password_recovery_page, name='password_recovery_page'),
    path('recover_password', views.recover_password, name='recover_password'),
    path('create_sdek_phone/<int:user_id>', views.create_sdek_phone, name='create_sdek_phone'),
    path('create_ozon_phone/<int:user_id>', views.create_ozon_phone, name='create_ozon_phone'),
    path('login_page_media_query', views.login_page_media_query, name='login_page_media_query'),
  
 
]