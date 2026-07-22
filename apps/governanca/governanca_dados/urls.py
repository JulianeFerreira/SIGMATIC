from django.urls import path
from . import views

urlpatterns = [
    path('nova_solicitacao/', views.nova_solicitacao_view, name='nova_solicitacao'),
    # Rotas novas para a equipe da CTIC/Governança:
    path('painel_solicitacoes/', views.painel_solicitacoes_view, name='painel_solicitacoes'),
    path('atualizar_status/<uuid:pk>/', views.atualizar_status_solicitacao, name='atualizar_status_solicitacao'),
]