from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.base.views import obter_modulos_dinamicos 

from .models import SolicitacaoAcesso
from .forms import SolicitacaoAcessoForm

# 1. VIEW DE CRIAÇÃO DA SOLICITAÇÃO
def nova_solicitacao_view(request):
    if request.method == 'POST':
        form = SolicitacaoAcessoForm(request.POST)
        
        if form.is_valid():
            solicitacao = form.save(commit=False)
            
            if request.user.is_authenticated:
                solicitacao.solicitante_sistema = request.user
            
            tipo_acesso = form.cleaned_data.get('tipo_acesso')
            
            if tipo_acesso == 'ANALISTA':
                solicitacao.dados_especificos = {
                    "banco_dados": request.POST.get('analista_banco_dados'),
                    "nome_usuario_banco": request.POST.get('analista_nome_usuario'),
                    "ip_origem": request.POST.get('analista_ip_origem'),
                    "justificativa": request.POST.get('analista_justificativa'),
                }
            elif tipo_acesso == 'APLICACAO':
                solicitacao.dados_especificos = {
                    "nome_sistema": request.POST.get('app_nome_sistema'),
                    "banco_dados": request.POST.get('app_banco_dados'),
                    "forma_acesso": request.POST.get('app_forma_acesso'),
                    "ip_origem": request.POST.get('app_ip_origem'),
                    "tabelas_campos": request.POST.get('app_tabelas_campos'),
                    "justificativa": request.POST.get('app_justificativa'),
                }
            
            solicitacao.status = 'CRIADA'
            solicitacao.save()
            
            messages.success(request, f"Solicitação encaminhada ao DPO com sucesso! Protocolo: #{str(solicitacao.id)[:8]}")
            return redirect(request.path)
            
        else:
            for campo, erros in form.errors.items():
                for erro in erros:
                    messages.error(request, f"{erro}")
    else:
        form = SolicitacaoAcessoForm()

    modulos, _ = obter_modulos_dinamicos()
    
    contexto = {
        'modulos': modulos,
        'base_url': '/governanca/governanca_dados',
        'url_atual': request.path,
        'form': form
    }
    
    return render(request, "governanca/governanca_dados/nova_solicitacao.html", contexto)


def painel_solicitacoes_view(request):
    modulos, _ = obter_modulos_dinamicos()
    
    solicitacoes = SolicitacaoAcesso.objects.all().order_by('-criado_em')

    contexto = {
        'modulos': modulos,
        'base_url': '/governanca/governanca_dados',
        'url_atual': request.path,
        'solicitacoes': solicitacoes,
    }

    return render(request, "governanca/governanca_dados/painel_solicitacoes.html", contexto)

def atualizar_status_solicitacao(request, pk):
    if request.method == 'POST':
        solicitacao = get_object_or_404(SolicitacaoAcesso, pk=pk)
        novo_status = request.POST.get('novo_status')
        parecer = request.POST.get('parecer_dpo', '')

        if novo_status:
            solicitacao.status = novo_status
            if parecer:
                solicitacao.parecer_dpo = parecer
            solicitacao.save()
            messages.success(request, f"Status da solicitação #{str(solicitacao.id)[:8]} atualizado com sucesso!")

    return redirect('/governanca/governanca_dados/painel_solicitacoes/')