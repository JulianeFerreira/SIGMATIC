# apps/base/urls.py
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.menu_principal, name='menu_principal'),
    path('pesquisa/', views.pesquisa, name='pesquisa'),
    
    path('<str:modulo>/<str:submodulo>/', views.carrega_submodulo_dinamico, name='carrega_submodulo_dinamico'),
    path('<str:modulo>/<str:nivel2>/<str:submodulo>/', views.carrega_submodulo_dinamico_profundo, name='carrega_submodulo_dinamico_profundo'),

    path('', include('apps.base.core.urls')),
]