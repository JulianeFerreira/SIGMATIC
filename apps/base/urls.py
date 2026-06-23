from django.urls import path, include
from . import views

urlpatterns = [
    # 1. Rotas estáticas
    path('', views.menu_principal, name='menu_principal'),
    path('pesquisa/', views.pesquisa, name='pesquisa'),
    
    # =======================================================
    # 2. O SISTEMA Contratações
    # =======================================================
    path('', include('apps.base.core.urls')),
    
    # =======================================================
    # 3. ROTAS DINÂMICAS
    # =======================================================
    path('<str:modulo>/<str:submodulo>/', views.carrega_submodulo_dinamico, name='carrega_submodulo_dinamico'),
    path('<str:modulo>/<str:nivel2>/<str:submodulo>/', views.carrega_submodulo_dinamico_profundo, name='carrega_submodulo_dinamico_profundo'),
]