from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('governanca/governanca_dados/', include('apps.governanca.governanca_dados.urls')),
    path('planejamento/pdtic/', include('apps.planejamento.pdtic.urls')),
    path('planejamento/pca/', include('apps.planejamento.pca.urls')),
    
    # Módulo de Contratações - Contratos
    path('contratacoes/contratos/', include('apps.contratacoes.contratos.urls')),
    
    # Rota raiz (deve ficar por último)
    path('', include('apps.base.urls')),
]
