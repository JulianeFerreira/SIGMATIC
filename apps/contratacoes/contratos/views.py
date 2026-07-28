from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Contrato
from .forms import ContratoForm

# ==========================================
# VIEWS DE INTERFACE (HTML)
# ==========================================

def painel_contratos_view(request):
    """Exibe a lista principal / painel de contratos."""
    contratos = Contrato.objects.all()
    # Aponta para: templates/contratacoes/contratos/contratos_lista.html
    return render(request, 'contratacoes/contratos/contratos_lista.html', {'contratos': contratos})


def novo_contrato_view(request):
    """Cadastra um novo contrato."""
    if request.method == 'POST':
        form = ContratoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('painel_contratos')
    else:
        form = ContratoForm()
    # Aponta para: templates/contratacoes/contratos/contratos_form.html
    return render(request, 'contratacoes/contratos/contratos_form.html', {'form': form, 'acao': 'Novo Contrato'})


def detalhe_contrato_view(request, pk=None):
    """Exibe a tela de acompanhamento (geral ou de um contrato específico)."""
    contrato = None
    if pk:
        contrato = get_object_or_404(Contrato, pk=pk)
    
    # Busca a lista de contratos para alimentar seletores/filtros na tela de acompanhamento, se necessário
    contratos = Contrato.objects.all()
    
    context = {
        'contrato': contrato,
        'contratos': contratos
    }
    return render(request, 'contratacoes/contratos/contratos_acompanhamentos.html', context)


def editar_contrato_view(request, pk):
    """Edita um contrato existente."""
    contrato = get_object_or_404(Contrato, pk=pk)
    if request.method == 'POST':
        form = ContratoForm(request.POST, instance=contrato)
        if form.is_valid():
            form.save()
            return redirect('detalhe_contrato', pk=contrato.pk)
    else:
        form = ContratoForm(instance=contrato)
    # Reutiliza o contratos_form.html para edição
    return render(request, 'contratacoes/contratos/contratos_form.html', {'form': form, 'contrato': contrato, 'acao': 'Editar Contrato'})


def dashboard_contratos_view(request):
    """Exibe o dashboard visual dos contratos."""
    # Aponta para: templates/contratacoes/contratos/contratos_dashboard.html
    return render(request, 'contratacoes/contratos/contratos_dashboard.html')


def relatorios_contratos_view(request):
    """Exibe os relatórios de contratos."""
    # Aponta para: templates/contratacoes/contratos/contratos_relatorios.html
    return render(request, 'contratacoes/contratos/contratos_relatorios.html')


def atualizar_status_contrato(request, pk):
    """Atualiza o status de um contrato via POST."""
    contrato = get_object_or_404(Contrato, pk=pk)
    if request.method == 'POST':
        novo_status = request.POST.get('status')
        if novo_status:
            contrato.status = novo_status
            contrato.save()
            return JsonResponse({'status': 'sucesso', 'novo_status': contrato.status})
    return JsonResponse({'status': 'erro'}, status=400)


# ==========================================
# ENDPOINTS DE API (JSON)
# ==========================================

def api_listar_contratos(request):
    contratos = list(Contrato.objects.values())
    return JsonResponse({'contratos': contratos}, safe=False)


def api_resumo_dashboard(request):
    total = Contrato.objects.count()
    return JsonResponse({'total_contratos': total})
