from django.urls import path
from apps.governanca.controle_de_acesso.views import dashboard_acessos_view

app_name = 'governanca'

urlpatterns = [
    # Rota do Dashboard de Controle de Acesso
    path('controle_de_acesso/dashboard/', dashboard_acessos_view, name='dashboard_acesso'),
]