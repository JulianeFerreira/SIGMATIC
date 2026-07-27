from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rota Base (Telas iniciais/Login) - Apenas uma vez!
    path('', include('apps.base.urls')),

    # Módulo de Governança
    path('governanca/', include('apps.governanca.urls')),
    path('governanca/controle_de_acesso/', include('apps.governanca.controle_de_acesso.urls')), # <- Sua pasta
    
    # Módulo de Planejamento
    path('planejamento/pdtic/', include('apps.planejamento.pdtic.urls')),
]