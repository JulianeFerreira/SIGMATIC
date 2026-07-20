from django.urls import path, include
from . import views

urlpatterns = [
    # 1. Rotas estáticas
    path('', views.menu_principal, name='menu_principal'),
    path('pesquisa/', views.pesquisa, name='pesquisa'),
    
# =======================================================
    # 2. O SISTEMA CONTRATAÇÕES (Mantemos por causa das APIs)
    # =======================================================
    path('', include('apps.base.core.urls')),
    
    # =======================================================
    # 3. ROTA UNIVERSAL (Cega para níveis de pasta)
    # =======================================================
    path('<path:caminho>/', views.carregar_template_dinamico, name='carregar_template_dinamico'),
]