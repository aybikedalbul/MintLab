from django.urls import path
from . import views

app_name = 'token_creator'

urlpatterns = [
    path('token_maker/', views.token_maker, name='token_maker'),
    path('', views.welcome, name='welcome'),
    path('about/', views.about, name='about'),
]