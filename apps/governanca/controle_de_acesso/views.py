import json
from django.shortcuts import render

def dashboard_acessos_view(request):
    labels_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    # Dados simulados das métricas (que depois virão do Banco de Dados)
    solicitadas_por_mes = [12, 19, 15, 22, 18, 25, 30, 10, 5, 20, 15, 8]
    aprovadas_por_mes = [10, 16, 14, 20, 16, 22, 28, 8, 4, 18, 12, 7]

    context = {
        'labels_meses_json': json.dumps(labels_meses),
        'solicitadas_json': json.dumps(solicitadas_por_mes),
        'aprovadas_json': json.dumps(aprovadas_por_mes),
    }

    return render(request, 'governanca/solicitacao_acesso/dashboard.html', context)
