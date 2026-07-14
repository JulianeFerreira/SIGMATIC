from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import date, datetime
from pathlib import Path
import json
import math
import pandas as pd

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt


def _current_user(request):
    if getattr(request, 'user', None) and request.user.is_authenticated:
        return {'name': request.user.get_username()}
    return {'name': 'Usuário'}


def _ctx(request, **kwargs):
    ctx = {'current_user': _current_user(request)}
    ctx.update(kwargs)
    return ctx


def _safe_str(v):
    if v is None:
        return ''
    if isinstance(v, float) and math.isnan(v):
        return ''
    return str(v).strip()


def _to_iso(v):
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    if hasattr(v, 'isoformat'):
        try:
            return v.isoformat()
        except Exception:
            pass
    s = str(v).strip()
    if not s or s.lower() == 'nan':
        return None
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except Exception:
            continue
    return s


def _money_to_float(v):
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if not s:
        return 0.0
    s = s.replace('R$', '').replace('.', '').replace(',', '.').strip()
    try:
        return float(s)
    except Exception:
        return 0.0


def _load_processos_from_excel():
    path = Path(settings.BASE_DIR) / 'GAA - Compras.xlsx'
    if not path.exists():
        return []
    try:
        df = pd.read_excel(path, sheet_name='Compras 2026', header=1)
    except Exception:
        return []
    df = df.dropna(how='all')
    processos = []
    for _, row in df.iterrows():
        numero = _safe_str(row.get('PROCESSO N°'))
        descricao = _safe_str(row.get('DESCRIÇÃO'))
        if not numero and not descricao:
            continue
        modalidade = _safe_str(row.get('MODALIDADE')) or 'Não informado'
        situacao = _safe_str(row.get('SITUAÇÃO')) or 'TRAMITANDO'
        observ = _safe_str(row.get('OBSERVAÇÃO'))
        conv = _safe_str(row.get('Convênio') or row.get('CONVÊNIO'))
        proc = {
            'processo_numero': numero,
            'descricao': descricao,
            'unidade_atendida': _safe_str(row.get('Unidade a ser atendida') or row.get('UNIDADE PCP') or row.get('UNIDADE')),
            'valor_previsto': _money_to_float(row.get('VALOR PREVISTO')),
            'modalidade': modalidade,
            'situacao': situacao,
            'data_criacao': _to_iso(row.get('DATA DE CRIAÇÃO')),
            'fonte_recurso': _safe_str(row.get('FONTE DE RECURSO') or row.get('VERBA')),
            'convenio': conv,
            'gestor': _safe_str(row.get('GESTOR')),
            'fiscal': _safe_str(row.get('FISCAL')),
            'instrucao_responsavel': _safe_str(row.get('instrução') or row.get('INSTRUÇÃO')),
            'onde_esta': _safe_str(row.get('ONDE ESTÁ')),
            'observacao': observ,
            'observacoes_adicionais': _safe_str(row.get('Observações')),
            'obs_extras': '',
            'data_pregao': _to_iso(row.get('DATA DO PREGÃO')),
            'contrato_assinado': _to_iso(row.get('CONTRATO ASSINADO')),
            'empenho_assinado': _to_iso(row.get('EMPENHO ASSINADO')),
            'empenho_contrato_enviado': _to_iso(row.get('EMPENHO E CONTRATO ENVIADO AO FORNECEDOR (DATA)') or row.get('EMPENHO ENVIADO AO FORNECEDOR (DATA)')),
            'prazo_entrega_dias': int(_money_to_float(row.get('PRAZO DE ENTREGA (DIAS)'))) if _safe_str(row.get('PRAZO DE ENTREGA (DIAS)')) else None,
            'data_prevista_entrega': _to_iso(row.get('DATA PREV. DE ENTREGA') or row.get('Data Máxima de entrega')),
            'material_entregue': _to_iso(row.get('MATERIAL ENTREGUE (DATA)')),
            'auditorias': [],
        }
        processos.append(proc)
    return processos


PROCESSOS = _load_processos_from_excel() or [
    {
        'processo_numero': '25.740.243-6', 'descricao': 'Aquisição de equipamento portátil de imagem multiespectral',
        'unidade_atendida': 'GAA / Compras', 'valor_previsto': 997000.0, 'modalidade': 'Inexigibilidade',
        'situacao': 'TRAMITANDO', 'data_criacao': '2026-04-01', 'fonte_recurso': 'INVESTIMENTO',
        'convenio': '', 'gestor': 'Raphael Maingue', 'fiscal': 'Eduarda Faria',
        'instrucao_responsavel': 'Setor de Compras', 'onde_esta': 'GAA', 'observacao': 'Processo em instrução.',
        'observacoes_adicionais': 'Aguardando documentação complementar.', 'obs_extras': '',
        'data_pregao': None, 'contrato_assinado': None, 'empenho_assinado': None,
        'empenho_contrato_enviado': None, 'prazo_entrega_dias': 60,
        'data_prevista_entrega': '2026-06-30', 'material_entregue': None, 'auditorias': []
    }
]

CONTRATOS = [
    {
        'gms': '1327/2024', 'numero_contrato': '01/2026', 'empresa': 'Empresa Alfa Ltda.',
        'categoria_servico': 'Vigilância Armada', 'local': 'Curitiba', 'quantidade': '12', 'posto': '24h',
        'data_inicio': '2026-01-01', 'data_termino': '2026-12-31', 'status_vigencia': 'vigente',
        'status_tramitacao': 'regular', 'status_financeiro': 'em_dia', 'status_ta': 'nao_aplicavel',
        'observacoes_ta': '', 'status_tap': '', 'ano_reajuste': '2026', 'numero_protocolo': '25.111.000-1',
        'descricao_tramitacao': 'Execução regular', 'localizacao_documento': 'GAA/Contratos',
        'data_tramitacao': '2026-02-10', 'observacoes_gerais': '', 'historico_alteracoes': ''
    },
    {
        'gms': '866/2024', 'numero_contrato': '02/2026', 'empresa': 'Empresa Beta S/A',
        'categoria_servico': 'Limpeza', 'local': 'Londrina', 'quantidade': '8', 'posto': '',
        'data_inicio': '2025-07-01', 'data_termino': '2026-05-10', 'status_vigencia': 'proximo_vencimento',
        'status_tramitacao': 'prorrogacao', 'status_financeiro': 'em_dia', 'status_ta': 'em_analise',
        'observacoes_ta': 'Prorrogação em estudo', 'status_tap': '', 'ano_reajuste': '2026',
        'numero_protocolo': '25.222.000-2', 'descricao_tramitacao': 'Prorrogação',
        'localizacao_documento': 'SESP/APCP', 'data_tramitacao': '2026-03-20', 'observacoes_gerais': '',
        'historico_alteracoes': ''
    },
]

BENS = [
    {
        'tombamento': 'PAT-001', 'descricao': 'Microscópio comparador balístico', 'situacao': 'em_uso',
        'categoria': 'Laboratório', 'marca': 'Leica', 'modelo': 'Forense', 'unidade_atual': 'UETC Curitiba Centro',
        'local_fisico': 'Sala 02', 'responsavel_nome': 'Servidor A', 'responsavel_matricula': '12345',
        'serial': 'ABC123', 'garantia_fim': '2026-12-31', 'movimentacoes': []
    },
    {
        'tombamento': 'PAT-002', 'descricao': 'Notebook administrativo', 'situacao': 'manutencao',
        'categoria': 'TI', 'marca': 'Dell', 'modelo': 'Latitude', 'unidade_atual': 'GAA', 'local_fisico': 'TI',
        'responsavel_nome': 'Servidor B', 'responsavel_matricula': '67890', 'serial': 'XYZ999',
        'garantia_fim': '2026-05-30', 'movimentacoes': []
    },
]

PCA_ITEMS = [
    {'numero_ordem': 1, 'tipo_item': 'Equipamento', 'categoria_contratacao': 'Tecnologia', 'descricao_objeto': 'Drone pericial', 'justificativa': 'Apoio pericial', 'valor_unitario': '150.000,00', 'valor_total': '150.000,00', 'grau_prioridade': 'Alta', 'data_pretendida': '2026-06', 'municipios': 'Curitiba', 'riscos_nao_contratacao': 'Perda operacional', 'renovacao_contrato': 'Não', 'modalidade_prevista': 'Pregão eletrônico', 'duracao_total': '12 meses', 'observacoes': ''},
    {'numero_ordem': 2, 'tipo_item': 'Serviço', 'categoria_contratacao': 'Infraestrutura', 'descricao_objeto': 'Manutenção predial', 'justificativa': 'Conservação das unidades', 'valor_unitario': '80.000,00', 'valor_total': '80.000,00', 'grau_prioridade': 'Média', 'data_pretendida': '2026-08', 'municipios': 'Matinhos', 'riscos_nao_contratacao': 'Interrupção das atividades', 'renovacao_contrato': 'Não', 'modalidade_prevista': 'Dispensa', 'duracao_total': '90 dias', 'observacoes': ''},
]


def _normalize_status(p):
    s = (p.get('situacao') or '').strip().lower()
    if 'final' in s or 'conclu' in s:
        return 'concluido'
    if 'arquiv' in s or 'cancel' in s:
        return 'concluido'
    if 'tram' in s or 'andamento' in s or 'exec' in s:
        return 'em_execucao'
    if 'atras' in s or 'pend' in s:
        return 'atrasado'
    return 'planejado'


def _extract_tipo(p):
    mod = (p.get('modalidade') or '').lower()
    if 'inexig' in mod:
        return 'Inexigibilidade'
    if 'dispensa' in mod:
        return 'Dispensa'
    if 'preg' in mod or 'licita' in mod or 'concorr' in mod or 'srp' in mod:
        return 'Licitação'
    return 'Outros'


def _extract_mes(p):
    raw = p.get('data_criacao') or p.get('data_prevista_entrega')
    if not raw:
        return 'Não informado'
    try:
        d = datetime.fromisoformat(str(raw)[:10])
        return ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'][d.month - 1]
    except Exception:
        return 'Não informado'


def home(request):
    return redirect('/') if request.path != '/' else render(request, 'contratacoes/compras/dashboard.html', _ctx(request))


def compras(request):
    return render(request, 'contratacoes/compras/dashboard.html', _ctx(request))


def compras_processos(request):
    return render(request, 'contratacoes/compras/processos.html', _ctx(request))


def compras_processo_novo(request):
    return render(request, 'contratacoes/compras/processo_form.html', _ctx(request))


def compras_processo_detail(request, processo_numero):
    return render(request, 'contratacoes/compras/processo_detail.html', _ctx(request, processo_numero=processo_numero))


def compras_relatorios(request):
    return render(request, 'contratacoes/compras/relatorios.html', _ctx(request))


def contratos(request):
    return render(request, 'contratacoes/contratos/contratos_dashboard.html', _ctx(request))


def contratos_lista(request):
    return render(request, 'contratacoes/contratos/contratos_lista.html', _ctx(request))


def contratos_form(request):
    return render(request, 'contratacoes/contratos/contratos_form.html', _ctx(request))


def contratos_relatorios(request):
    return render(request, 'contratacoes/contratos/contratos_relatorios.html', _ctx(request))


def patrimonio(request):
    return render(request, 'patrimonio/dashboard.html', _ctx(request))


def patrimonio_bens(request):
    return render(request, 'patrimonio/bens_lista.html', _ctx(request))


def patrimonio_bem_novo(request):
    return render(request, 'patrimonio/bem_form.html', _ctx(request))


def patrimonio_bem_detail(request, tombamento):
    return render(request, 'patrimonio/bem_detail.html', _ctx(request, tombamento=tombamento))


def patrimonio_relatorios(request):
    return render(request, 'patrimonio/relatorios.html', _ctx(request))


def planejamento(request):
    return render(request, 'planejamento/dashboard.html', _ctx(request))


def pca(request):
    return render(request, 'planejamento/pca/pca.html', _ctx(request))


def configuracoes(request):
    return render(request, 'configuracoes.html', _ctx(request))


def dashboard_metricas(request):
    total = len(PROCESSOS)
    finalizados = sum(1 for p in PROCESSOS if _normalize_status(p) == 'concluido')
    tramitando = sum(1 for p in PROCESSOS if _normalize_status(p) == 'em_execucao')
    atrasados = sum(1 for p in PROCESSOS if _normalize_status(p) == 'atrasado')
    valor_total = sum(float(p.get('valor_previsto') or 0) for p in PROCESSOS)
    arquivados = sum(1 for p in PROCESSOS if 'arquiv' in (p.get('situacao') or '').lower())
    return JsonResponse({
        'total_processos': total,
        'valor_total_previsto': valor_total,
        'processos_finalizados': finalizados,
        'processos_tramitando': tramitando,
        'processos_atrasados': atrasados,
        'processos_arquivados': arquivados,
    })


def dashboard_modalidade(request):
    counter = Counter((p.get('modalidade') or 'Não informado') for p in PROCESSOS)
    return JsonResponse([{'modalidade': k, 'quantidade': v} for k, v in counter.items()], safe=False)


def dashboard_situacao(request):
    counter = Counter((p.get('situacao') or 'Não informado') for p in PROCESSOS)
    return JsonResponse([{'situacao': k, 'quantidade': v} for k, v in counter.items()], safe=False)


def dashboard_criacao_por_mes(request):
    counter = Counter(_extract_mes(p) for p in PROCESSOS)
    ordem = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez','Não informado']
    return JsonResponse([{'mes': m, 'quantidade': counter.get(m, 0)} for m in ordem if counter.get(m, 0)], safe=False)


def processos_api(request):
    if request.method == 'GET':
        busca = (request.GET.get('busca') or '').lower()
        situacao = (request.GET.get('situacao') or '').lower()
        modalidade = (request.GET.get('modalidade') or '').lower()
        data = []
        for p in PROCESSOS:
            if busca and busca not in (str(p['processo_numero']) + ' ' + str(p['descricao'])).lower():
                continue
            if situacao and situacao not in (p['situacao'] or '').lower():
                continue
            if modalidade and modalidade not in (p['modalidade'] or '').lower():
                continue
            data.append(p)
        return JsonResponse(data, safe=False)

    if request.method == 'POST':
        try:
            payload = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'JSON inválido.'}, status=400)
        payload.setdefault('auditorias', [])
        PROCESSOS.insert(0, payload)
        return JsonResponse(payload, status=201)

    return JsonResponse({'detail': 'Método não permitido.'}, status=405)


def processo_api_detail(request, processo_numero):
    item = next((p for p in PROCESSOS if str(p['processo_numero']) == str(processo_numero)), None)
    if not item:
        return JsonResponse({'detail': 'Processo não encontrado.'}, status=404)
    return JsonResponse(item)


@csrf_exempt
def contratos_api(request):
    if request.method == 'GET':
        empresa = (request.GET.get('empresa') or '').lower()
        categoria = (request.GET.get('categoria_servico') or '').lower()
        local = (request.GET.get('local') or '').lower()
        status_vig = (request.GET.get('status_vigencia') or '').lower()
        status_tram = (request.GET.get('status_tramitacao') or '').lower()
        data = []
        for c in CONTRATOS:
            if empresa and empresa not in (c.get('empresa') or '').lower():
                continue
            if categoria and categoria not in (c.get('categoria_servico') or '').lower():
                continue
            if local and local not in (c.get('local') or '').lower():
                continue
            if status_vig and status_vig not in (c.get('status_vigencia') or '').lower():
                continue
            if status_tram and status_tram not in (c.get('status_tramitacao') or '').lower():
                continue
            data.append(c)
        return JsonResponse(data, safe=False)

    if request.method == 'POST':
        try:
            payload = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'JSON inválido.'}, status=400)
        CONTRATOS.insert(0, payload)
        return JsonResponse(payload, status=201)

    return JsonResponse({'detail': 'Método não permitido.'}, status=405)


def contratos_metricas(request):
    total = len(CONTRATOS)
    vigentes = sum(1 for c in CONTRATOS if c.get('status_vigencia') == 'vigente')
    prox = sum(1 for c in CONTRATOS if c.get('status_vigencia') == 'proximo_vencimento')
    vencidos = sum(1 for c in CONTRATOS if c.get('status_vigencia') == 'vencido')
    prorrogados = sum(1 for c in CONTRATOS if c.get('status_tramitacao') == 'prorrogacao')
    rescindidos = sum(1 for c in CONTRATOS if c.get('status_tramitacao') == 'rescindido')
    por_categoria = Counter(c.get('categoria_servico') or 'Não informado' for c in CONTRATOS)
    por_status = Counter(c.get('status_tramitacao') or 'Não informado' for c in CONTRATOS)
    return JsonResponse({
        'total_contratos': total,
        'vigentes': vigentes,
        'proximo_vencimento': prox,
        'vencidos': vencidos,
        'prorrogados': prorrogados,
        'rescindidos': rescindidos,
        'por_categoria': [{'categoria': k, 'quantidade': v} for k, v in por_categoria.items()],
        'por_status_tramitacao': [{'status': k, 'quantidade': v} for k, v in por_status.items()],
    })


def patrimonio_kpis(request):
    total = len(BENS)
    ativos = sum(1 for b in BENS if b.get('situacao') == 'em_uso')
    sem_resp = sum(1 for b in BENS if not b.get('responsavel_nome'))
    sem_local = sum(1 for b in BENS if not b.get('local_fisico'))
    manut = sum(1 for b in BENS if b.get('situacao') == 'manutencao')
    garantia = sum(1 for b in BENS if b.get('garantia_fim'))
    return JsonResponse({
        'total_bens': total,
        'total_ativos': ativos,
        'sem_responsavel': sem_resp,
        'sem_local': sem_local,
        'em_manutencao': manut,
        'garantia_ate_60d': garantia,
    })


@csrf_exempt
def patrimonio_bens_api(request):
    if request.method == 'GET':
        q = (request.GET.get('q') or '').lower()
        situacao = (request.GET.get('situacao') or '').lower()
        unidade = (request.GET.get('unidade') or '').lower()
        data = []
        for b in BENS:
            if q and q not in ' '.join([str(b.get('tombamento','')), str(b.get('descricao','')), str(b.get('categoria',''))]).lower():
                continue
            if situacao and situacao not in (b.get('situacao') or '').lower():
                continue
            if unidade and unidade not in (b.get('unidade_atual') or '').lower():
                continue
            data.append(b)
        return JsonResponse(data, safe=False)
    if request.method == 'POST':
        try:
            payload = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'JSON inválido.'}, status=400)
        payload.setdefault('movimentacoes', [])
        BENS.insert(0, payload)
        return JsonResponse(payload, status=201)
    return JsonResponse({'detail': 'Método não permitido.'}, status=405)


def patrimonio_bem_api(request, tombamento):
    item = next((deepcopy(b) for b in BENS if str(b['tombamento']) == str(tombamento)), None)
    if not item:
        return JsonResponse({'detail': 'Bem não encontrado.'}, status=404)
    return JsonResponse(item)


@csrf_exempt
def patrimonio_transferir_api(request, tombamento):
    item = next((b for b in BENS if str(b['tombamento']) == str(tombamento)), None)
    if not item:
        return JsonResponse({'detail': 'Bem não encontrado.'}, status=404)
    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'JSON inválido.'}, status=400)
    origem = item.get('unidade_atual', '')
    destino = payload.get('para_unidade') or origem
    item.setdefault('movimentacoes', []).append({
        'data': datetime.now().isoformat(),
        'tipo': 'Transferência',
        'de_unidade': origem,
        'para_unidade': destino,
        'motivo': payload.get('motivo', ''),
        'usuario': _current_user(request)['name'],
    })
    item['unidade_atual'] = destino
    return JsonResponse({'ok': True})


def planejamento_metrics(request):
    total = len(PROCESSOS)
    valor_planejado = sum(float(p.get('valor_previsto') or 0) for p in PROCESSOS)
    normalized = [_normalize_status(p) for p in PROCESSOS]
    em_execucao = sum(1 for s in normalized if s == 'em_execucao')
    concluidos = sum(1 for s in normalized if s == 'concluido')
    atrasados = sum(1 for s in normalized if s == 'atrasado')
    planejados = sum(1 for s in normalized if s == 'planejado')
    prioritarias = sum(1 for p in PROCESSOS if any(k in (p.get('descricao') or '').lower() for k in ['urg', 'prior', 'emerg']))
    emenda = sum(1 for p in PROCESSOS if p.get('convenio'))
    execucao_percentual = round(((em_execucao + concluidos) / total) * 100, 1) if total else 0
    return JsonResponse({
        'total_demandas': total,
        'valor_planejado': valor_planejado,
        'demandas_prioritarias': prioritarias,
        'demandas_emenda': emenda,
        'planejados': planejados,
        'em_execucao': em_execucao,
        'concluidos': concluidos,
        'atrasados': atrasados,
        'execucao_percentual': execucao_percentual,
    })


def planejamento_por_unidade(request):
    top = int(request.GET.get('top', 10))
    counter = Counter((p.get('unidade_atendida') or 'Não informado') for p in PROCESSOS)
    return JsonResponse([{'unidade': k, 'quantidade': v} for k, v in counter.most_common(top)], safe=False)


def planejamento_por_modalidade(request):
    counter = Counter((p.get('modalidade') or 'Não informado') for p in PROCESSOS)
    return JsonResponse([{'modalidade': k, 'quantidade': v} for k, v in counter.most_common()], safe=False)


def planejamento_por_fonte_recurso(request):
    counter = Counter((p.get('fonte_recurso') or 'Não informado') for p in PROCESSOS)
    return JsonResponse([{'fonte_recurso': k, 'quantidade': v} for k, v in counter.most_common()], safe=False)


def planejamento_por_mes(request):
    counter = Counter(_extract_mes(p) for p in PROCESSOS)
    ordem = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez','Não informado']
    return JsonResponse([{'mes': m, 'quantidade': counter.get(m, 0)} for m in ordem if counter.get(m, 0) > 0], safe=False)


def planejamento_top_tipos(request):
    top = int(request.GET.get('top', 8))
    counter = Counter(_extract_tipo(p) for p in PROCESSOS)
    return JsonResponse([{'tipo': k, 'quantidade': v} for k, v in counter.most_common(top)], safe=False)


def planejamento_alertas(request):
    limit = int(request.GET.get('limit', 8))
    hoje = date.today()
    alertas = []
    for p in PROCESSOS:
        status = _normalize_status(p)
        prazo = p.get('data_prevista_entrega') or p.get('data_pregao')
        dias = None
        if prazo:
            try:
                dias = (datetime.fromisoformat(str(prazo)[:10]).date() - hoje).days
            except Exception:
                dias = None
        if status == 'atrasado':
            alertas.append({'tipo': 'atrasado', 'processo': p.get('processo_numero'), 'descricao': p.get('descricao'), 'mensagem': f"Processo {p.get('processo_numero')} com indício de atraso.", 'dias': dias})
        elif dias is not None and dias <= 30:
            alertas.append({'tipo': 'atencao', 'processo': p.get('processo_numero'), 'descricao': p.get('descricao'), 'mensagem': f"Processo {p.get('processo_numero')} com marco próximo ({dias} dias).", 'dias': dias})
    prioridade = {'atrasado': 0, 'atencao': 1}
    alertas.sort(key=lambda x: (prioridade.get(x['tipo'], 9), 999999 if x['dias'] is None else x['dias']))
    return JsonResponse(alertas[:limit], safe=False)


def planejamento_lista(request):
    skip = int(request.GET.get('skip', 0))
    limit = int(request.GET.get('limit', 20))
    unidade = (request.GET.get('unidade') or '').lower().strip()
    busca = (request.GET.get('busca') or '').lower().strip()
    status = (request.GET.get('status') or '').lower().strip()
    itens = []
    for p in PROCESSOS:
        item = {
            'numero_processo': p.get('processo_numero'),
            'descricao': p.get('descricao'),
            'unidade_estimada': p.get('unidade_atendida') or 'Não informado',
            'modalidade': p.get('modalidade') or 'Não informado',
            'fonte_recurso': p.get('fonte_recurso') or 'Não informado',
            'valor_previsto': float(p.get('valor_previsto') or 0),
            'prazo_entrega_dias': p.get('prazo_entrega_dias'),
            'status': _normalize_status(p),
            'observacao': ' | '.join(filter(None, [p.get('observacao'), p.get('observacoes_adicionais'), p.get('obs_extras')])),
        }
        itens.append(item)
    if unidade:
        itens = [x for x in itens if unidade in (x.get('unidade_estimada') or '').lower()]
    if busca:
        itens = [x for x in itens if busca in ' '.join([str(x.get('numero_processo') or ''), str(x.get('descricao') or ''), str(x.get('observacao') or ''), str(x.get('modalidade') or '')]).lower()]
    if status:
        itens = [x for x in itens if x.get('status') == status]
    total = len(itens)
    return JsonResponse({'total': total, 'itens': itens[skip: skip + limit]})


def pca_metrics(request):
    total = len(PCA_ITEMS)
    valor = sum(_money_to_float(x.get('valor_total')) for x in PCA_ITEMS)
    top = Counter((x.get('tipo_item') or 'Não informado') for x in PCA_ITEMS).most_common(5)
    return JsonResponse({'total_itens': total, 'valor_total_estimado': valor, 'top_tipos': [{'tipo_item': k, 'quantidade': v} for k, v in top]})


def pca_lista(request):
    skip = int(request.GET.get('skip', 0))
    limit = int(request.GET.get('limit', 50))
    tipo_item = (request.GET.get('tipo_item') or '').lower().strip()
    numero_ordem = request.GET.get('numero_ordem')
    busca = (request.GET.get('busca') or '').lower().strip()
    itens = PCA_ITEMS
    if numero_ordem:
        itens = [x for x in itens if str(x.get('numero_ordem')) == str(numero_ordem)]
    if tipo_item:
        itens = [x for x in itens if tipo_item in (x.get('tipo_item') or '').lower()]
    if busca:
        itens = [x for x in itens if busca in ' '.join([str(x.get('descricao_objeto') or ''), str(x.get('justificativa') or ''), str(x.get('observacoes') or '')]).lower()]
    total = len(itens)
    return JsonResponse({'total': total, 'itens': itens[skip: skip + limit]})


def pca_detail(request, numero_ordem):
    it = next((x for x in PCA_ITEMS if int(x.get('numero_ordem')) == int(numero_ordem)), None)
    if not it:
        return JsonResponse({'detail': 'Item não encontrado.'}, status=404)
    return JsonResponse(it)


import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ModuloSistema

@csrf_exempt
def gateway_roteador(request, nome_modulo, caminho_restante):
    try:
        modulo = ModuloSistema.objects.get(slug=nome_modulo)
        if not modulo.ativo:
            return JsonResponse({"erro": f"O módulo '{modulo.nome}' está em manutenção."}, status=503)

        url_destino = f"{modulo.url_destino.rstrip('/')}/{caminho_restante}"
        
        try:
            resposta = requests.request(
                method=request.method,
                url=url_destino,
                params=request.GET,
                data=request.body if request.body else None,
                headers={'Content-Type': request.headers.get('Content-Type', 'application/json')},
                timeout=10
            )
            return HttpResponse(content=resposta.content, status=resposta.status_code, content_type=resposta.headers.get('Content-Type', 'application/json'))
        except requests.exceptions.RequestException:
            return JsonResponse({"erro": f"Módulo '{modulo.nome}' offline."}, status=502)

    except ModuloSistema.DoesNotExist:
        return JsonResponse({"erro": f"Módulo '{nome_modulo}' não cadastrado no Core."}, status=404)