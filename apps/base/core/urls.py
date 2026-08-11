from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Navegação principal
    path('compras/', views.compras, name='compras'),
    path('contratos/', views.contratos, name='contratos'),
    path('patrimonio/', views.patrimonio, name='patrimonio'),
    path('planejamento/', views.planejamento, name='planejamento'),
    path('configuracoes/', views.configuracoes, name='configuracoes'),

    # UI legada adaptada
    path('ui/configuracoes/', views.configuracoes, name='ui_configuracoes'),

    # Compras
    path('ui/dashboard/', views.compras, name='compras_dashboard'),
    path('ui/processos/', views.compras_processos, name='processos_lista'),
    path('ui/processos/novo/', views.compras_processo_novo, name='processo_novo'),
    path('ui/processos/<str:processo_numero>/', views.compras_processo_detail, name='processo_detail'),
    path('ui/relatorios/', views.compras_relatorios, name='compras_relatorios'),

    # Contratos
    path('ui/contratos/', views.contratos, name='contratos_dashboard'),
    path('ui/contratos/lista/', views.contratos_lista, name='contratos_lista'),
    path('ui/contratos/novo/', views.contratos_form, name='contratos_form'),
    path('ui/contratos/acompanhamento/', views.contratos_acompanhamento, name='contrato_acompanhamento'),
    path('ui/contratos/relatorios/', views.contratos_relatorios, name='contratos_relatorios'),

    # Patrimônio
    path('ui/patrimonio/', views.patrimonio, name='patrimonio_dashboard'),
    path('ui/patrimonio/bens/', views.patrimonio_bens, name='patrimonio_bens'),
    path('ui/patrimonio/bens/novo/', views.patrimonio_bem_novo, name='patrimonio_bem_novo'),
    path('ui/patrimonio/bens/<str:tombamento>/', views.patrimonio_bem_detail, name='patrimonio_bem_detail'),
    path('ui/patrimonio/relatorios/', views.patrimonio_relatorios, name='patrimonio_relatorios'),

    # Planejamento
    path('ui/planejamento/', views.planejamento, name='planejamento_dashboard'),
    path('ui/planejamento/pca/', views.pca, name='pca_lista'),

    # APIs - Compras
    path('dashboard/metricas', views.dashboard_metricas, name='dashboard_metricas'),
    path('dashboard/modalidade', views.dashboard_modalidade, name='dashboard_modalidade'),
    path('dashboard/situacao', views.dashboard_situacao, name='dashboard_situacao'),
    path('dashboard/criacao-por-mes', views.dashboard_criacao_por_mes, name='dashboard_criacao_por_mes'),
    path('processos', views.processos_api, name='processos_api'),
    path('processos/<str:processo_numero>', views.processo_api_detail, name='processo_api_detail'),

    # APIs - Contratos
    path('contratos', views.contratos_api, name='contratos_api'),
    path('contratos/dashboard/metricas', views.contratos_metricas, name='contratos_metricas'),
    path('contratos_api', views.contratos_api, name='contratos_api_alt'),
    path('contratos/data', views.contratos_api, name='contratos_api_data'),

    # APIs - Patrimônio
    path('api/patrimonio/kpis', views.patrimonio_kpis, name='patrimonio_kpis'),
    path('api/patrimonio/bens', views.patrimonio_bens_api, name='patrimonio_bens_api'),
    path('api/patrimonio/bens/<str:tombamento>', views.patrimonio_bem_api, name='patrimonio_bem_api'),
    path('api/patrimonio/bens/<str:tombamento>/transferir', views.patrimonio_transferir_api, name='patrimonio_transferir_api'),

    # APIs - Planejamento / PCA
    path('api/planejamento/metrics', views.planejamento_metrics, name='planejamento_metrics'),
    path('api/planejamento/por_unidade', views.planejamento_por_unidade, name='planejamento_por_unidade'),
    path('api/planejamento/por_modalidade', views.planejamento_por_modalidade, name='planejamento_por_modalidade'),
    path('api/planejamento/por_fonte_recurso', views.planejamento_por_fonte_recurso, name='planejamento_por_fonte_recurso'),
    path('api/planejamento/por_mes', views.planejamento_por_mes, name='planejamento_por_mes'),
    path('api/planejamento/top_tipos', views.planejamento_top_tipos, name='planejamento_top_tipos'),
    path('api/planejamento/alertas', views.planejamento_alertas, name='planejamento_alertas'),
    path('api/planejamento/lista', views.planejamento_lista, name='planejamento_lista'),
    path('api/pca/metrics', views.pca_metrics, name='pca_metrics'),
    path('api/pca/lista', views.pca_lista, name='pca_lista_api'),
    path('api/pca/<int:numero_ordem>', views.pca_detail, name='pca_detail_api'),
]

path('api/pca/metrics', views.pca_metrics, name='pca_metrics'),
path('api/pca/lista', views.pca_lista, name='pca_lista_api'),
path('api/pca/<int:numero_ordem>', views.pca_detail, name='pca_detail_api'),
path('api/gateway/<str:nome_modulo>/<path:caminho_restante>', views.gateway_roteador, name='gateway_roteador'),
