import json
from django.shortcuts import render

def dashboard_acessos_view(request):
    """
    View responsável pelas métricas e gráficos do Dashboard de Controle de Acesso (Visão Anual).
    """
    # 12 meses do ano
    labels_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    # Exemplo com 12 valores (Jan a Jun com dados, Jul a Dez zerados para preencher o ano)
    solicitadas_por_mes = [12, 19, 15, 22, 18, 25, 0, 0, 0, 0, 0, 0]
    aprovadas_por_mes   = [10, 16, 14, 20, 16, 22, 0, 0, 0, 0, 0, 0]

    context = {
        'labels_meses_json': json.dumps(labels_meses),
        'solicitadas_json': json.dumps(solicitadas_por_mes),
        'aprovadas_json': json.dumps(aprovadas_por_mes),
    }

    return render(request, 'governanca/controle_de_acesso/dashboard.html', context)
