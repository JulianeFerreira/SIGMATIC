from django.urls import path
from . import views

urlpatterns = [
    # 1. A rota que carrega a tela (HTML)
    path('', views.painel_pca_view, name='painel_pca'),
    
    # 2. As rotas de API que retornam JSON (usadas pelos botões e gráficos na tela)
    path('api/importar/', views.import_pca, name='pca_importar'),
    path('api/metricas/', views.pca_metrics, name='pca_metricas'),
    path('api/lista/', views.pca_lista, name='pca_lista'),
    path('api/detalhe/<int:numero_ordem>/', views.pca_detail, name='pca_detalhe'),
]