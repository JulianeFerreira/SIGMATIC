function formatCurrencyBRL(value) {
    return Number(value || 0).toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    });
}

function formatDateBR(value) {
    if (!value) return '';
    try {
        return new Date(value).toLocaleDateString('pt-BR');
    } catch {
        return value;
    }
}

function escapeHTML(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) {
        el.innerText = value || '';
    }
}

function preencherTimeline(processo) {
    const eventos = [
        { field: 'data_criacao', label: 'Criação do Processo' },
        { field: 'data_pregao', label: 'Data do Pregão' },
        { field: 'contrato_assinado', label: 'Contrato Assinado' },
        { field: 'empenho_assinado', label: 'Empenho Assinado' },
        { field: 'empenho_contrato_enviado', label: 'Enviado ao Fornecedor' },
        { field: 'data_prevista_entrega', label: 'Entrega Prevista' },
        { field: 'material_entregue', label: 'Material Entregue' }
    ];

    const container = document.getElementById('timeline');
    if (!container) return;

    container.innerHTML = '';

    eventos.forEach(ev => {
        const value = processo[ev.field];

        if (!value) return;

        const item = document.createElement('div');
        item.className = 'timeline-item';

        item.innerHTML = `
            <div class="timeline-dot"></div>
            <div class="timeline-content">
                <div class="timeline-label">${escapeHTML(ev.label)}</div>
                <div class="timeline-date">${formatDateBR(value)}</div>
            </div>
        `;

        container.appendChild(item);
    });

    if (!container.children.length) {
        container.innerHTML = `
            <p class="detail-note-text text-muted">
                Nenhuma data registrada no cronograma.
            </p>
        `;
    }
}

function preencherAuditoria(auditorias) {
    const tbody = document.getElementById('tabela-auditoria');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (!auditorias || !auditorias.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-muted">
                    Nenhum registro de auditoria.
                </td>
            </tr>
        `;
        return;
    }

    auditorias.forEach(a => {
        const tr = document.createElement('tr');
        const data = a.data ? new Date(a.data).toLocaleString('pt-BR') : '';

        tr.innerHTML = `
            <td>${escapeHTML(data)}</td>
            <td>${escapeHTML(a.campo)}</td>
            <td>${escapeHTML(a.valor_antigo || '')}</td>
            <td>${escapeHTML(a.valor_novo || '')}</td>
            <td>${escapeHTML(a.usuario || '')}</td>
        `;

        tbody.appendChild(tr);
    });
}

async function carregarDetalhes() {
    const main = document.querySelector('main[data-processo-numero]');
    const numero = main?.dataset?.processoNumero;

    if (!numero) {
        alert('Número do processo não encontrado na página.');
        return;
    }

    const resp = await fetch(`/processos/${encodeURIComponent(numero)}`);

    if (!resp.ok) {
        alert('Não foi possível carregar o processo.');
        return;
    }

    const p = await resp.json();

    document.getElementById('tituloProcesso').innerText = `Processo ${p.processo_numero || numero}`;
    document.getElementById('subtituloProcesso').innerText = p.descricao || '';

    setText('det-numero', p.processo_numero);
    setText('det-data-criacao', formatDateBR(p.data_criacao));

    const situacaoSpan = document.getElementById('det-situacao');
    if (situacaoSpan) {
        const situacao = p.situacao || '';
        situacaoSpan.innerText = situacao || '—';
        situacaoSpan.className = `status-pill status-${situacao}`;
    }

    setText('det-unidade', p.unidade_atendida);
    setText('det-onde-esta', p.onde_esta);

    setText('det-valor', formatCurrencyBRL(p.valor_previsto));
    setText('det-fonte', p.fonte_recurso);
    setText('det-modalidade', p.modalidade);
    setText('det-convenio', p.convenio);

    setText('det-gestor', p.gestor);
    setText('det-fiscal', p.fiscal);
    setText('det-instrucao', p.instrucao_responsavel);

    setText('det-observacao', p.observacao);
    setText('det-obs-adicionais', p.observacoes_adicionais);
    setText('det-obs-extras', p.obs_extras);

    preencherTimeline(p);
    preencherAuditoria(p.auditorias || []);
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('btnVoltar')?.addEventListener('click', () => {
        window.location.href = '/ui/processos/';
    });

    carregarDetalhes().catch(err => {
        console.error(err);
        alert('Erro ao carregar detalhes do processo.');
    });
});
