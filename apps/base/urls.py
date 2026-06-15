# apps/base/urls.py
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.menu_principal, name='menu_principal'),
    
    # 2. O Gateway Dinâmico
    path('api/gateway/<str:nome_modulo>/<path:caminho_restante>', views.gateway_base_roteador, name='gateway_base_roteador'),

    path('', include('apps.base.core.urls')),
]