# apps/base/urls.py
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.menu_principal, name='menu_principal'),
    
    path('pesquisa/', views.pesquisa, name='pesquisa'),
    
    path('', include('apps.base.core.urls')),
]