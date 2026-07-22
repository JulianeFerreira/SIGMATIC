from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.base.urls')),
    
    # Redireciona tudo que começa com 'governanca/' para as urls do app governança
    path('governanca/', include('apps.governanca.urls')),
    path('governanca/governanca_dados/', include('apps.governanca.governanca_dados.urls')),
    path('planejamento/pdtic/', include('apps.planejamento.pdtic.urls')),
    path('', include('apps.base.urls')),
    
]