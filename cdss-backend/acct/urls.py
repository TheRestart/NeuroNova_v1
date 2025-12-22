from django.urls import path
from . import views

app_name = 'acct'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('me/', views.me, name='me'),
]
