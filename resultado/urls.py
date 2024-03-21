 # Criando URLS padrões para acesso.
from django.urls import path, include
from django.urls import path
from . import views

urlpatterns = [
    path('',views.homepage, name='home'),
    path('search_page/', views.search),
    path('return_page/', views.all_results, name='return_page'),
]