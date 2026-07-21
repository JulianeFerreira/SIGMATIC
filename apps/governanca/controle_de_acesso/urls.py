# apps/governanca/controle_de_acesso/urls.py
from django.urls import path
from .views import dashboard_acessos_view

urlpatterns = [
    path('dashboard/', dashboard_acessos_view, name='dashboard_acesso'),
]