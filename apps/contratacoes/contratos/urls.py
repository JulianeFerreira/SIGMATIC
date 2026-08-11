from django.urls import path
from . import views

urlpatterns = [
    # Navegação Principal (Abas)
    path('', views.painel_contratos_view, name='painel_contratos_index'),
    path('painel_contratos/', views.painel_contratos_view, name='painel_contratos'),
    path('dashboard/', views.dashboard_contratos_view, name='dashboard_contratos'),
    path('relatorios/', views.relatorios_contratos_view, name='relatorios_contratos'),
    
    # Rota da Aba Acompanhamento (Acesso Direto pela Aba ou com ID do Contrato)
    path('acompanhamento/', views.detalhe_contrato_view, name='acompanhamento_contratos'),
    path('acompanhamento/<uuid:pk>/', views.detalhe_contrato_view, name='detalhe_contrato'),

    # Formulários e Ações
    path('novo_contrato/', views.novo_contrato_view, name='novo_contrato'),
    path('editar_contrato/<uuid:pk>/', views.editar_contrato_view, name='editar_contrato'),
    path('atualizar_status_contrato/<uuid:pk>/', views.atualizar_status_contrato, name='atualizar_status_contrato'),

    # APIs
    path('api_listar_contratos/', views.api_listar_contratos, name='api_listar_contratos'),
    path('api_resumo_dashboard/', views.api_resumo_dashboard, name='api_resumo_dashboard'),
]
