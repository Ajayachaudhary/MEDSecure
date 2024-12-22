from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('handle-login/', views.handle_login, name='handle-login'),
    path('handle-signup/', views.handle_signup, name='handle-signup'),
    path('logout/', views.handle_logout, name='handle-logout'), 
]
