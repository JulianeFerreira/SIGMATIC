
# apps/governanca/controle_de_acesso/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard_acessos_view, name='dashboard_acesso'),
    
    # Solicitações (Comentado temporariamente)
     path('nova_solicitacao/', views.nova_solicitacao_view, name='nova_solicitacao'),
    
    # Rotas para a equipe da CTIC/Governança (Comentado temporariamente)
     path('painel_solicitacoes/', views.painel_solicitacoes_view, name='painel_solicitacoes'),
     path('atualizar_status/<uuid:pk>/', views.atualizar_status_solicitacao, name='atualizar_status_solicitacao'),
]