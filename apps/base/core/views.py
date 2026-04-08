from django.shortcuts import render

def home(request):
    return render(request, 'configuracoes.html')

def compras(request):
    return render(request, 'compras/dashboard.html')

def contratos(request):
    return render(request, 'contratos/contratos_dashboard.html')

def patrimonio(request):
    return render(request, 'patrimonio/dashboard.html')

def planejamento(request):
    return render(request, 'planejamento/dashboard.html')
