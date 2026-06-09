function formatCurrencyBRL(value) {
    return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function formatDateBR(d) {
    if (!d) return '';
    try {
        return new Date(d).toLocaleDateString('pt-BR');
    } catch {
        return d;
    }
}

function setText(id, value) {
    document.getElementById(id).innerText = value || '';
}

function preencherTimeline(processo) {
    const eventos = [
        { field: 'data_criacao', label: 'Criação do Processo' },
        { field: 'data_pregao', label: 'Data do Pregão' },
        { field: 'contrato_assinado', label: 'Contrato Assinado' },
        { field: 'empenho_assinado', label: 'Empenho Assinado' },
        { field: 'empenho_contrato_enviado', label: 'Enviado ao Fornecedor' },
        { field: 'data_prevista_entrega', label: 'Entrega Prevista' },
        { field: 'material_entregue', label: 'Material Entregue' },
    ];

    const container = document.getElementById('timeline');
    container.innerHTML = '';

    eventos.forEach(ev => {
        const value = processo[ev.field];
        if (!value) return;

        const item = document.createElement('div');
        item.className = 'timeline-item';
        item.innerHTML = `
            <div class="timeline-dot"></div>
            <div class="timeline-content">
                <div class="timeline-label">${ev.label}</div>
                <div class="timeline-date">${formatDateBR(value)}</div>
            </div>
        `;
        container.appendChild(item);
    });

    if (!container.children.length) {
        container.innerHTML = '<p class="detail-note-text">Nenhuma data registrada no cronograma.</p>';
    }
}

function preencherAuditoria(auditorias) {
    const tbody = document.getElementById('tabela-auditoria');
    tbody.innerHTML = '';

    if (!auditorias || !auditorias.length) {
        const tr = document.createElement('tr');
        tr.innerHTML = '<td colspan="5">Nenhum registro de auditoria.</td>';
        tbody.appendChild(tr);
        return;
    }

    auditorias.forEach(a => {
        const tr = document.createElement('tr');
        const data = a.data ? new Date(a.data).toLocaleString('pt-BR') : '';
        tr.innerHTML = `
            <td>${data}</td>
            <td>${a.campo}</td>
            <td>${a.valor_antigo || ''}</td>
            <td>${a.valor_novo || ''}</td>
            <td>${a.usuario || ''}</td>
        `;
        tbody.appendChild(tr);
    });
}

async function carregarDetalhes() {
    const main = document.querySelector('main');
    const numero = main.dataset.processoNumero;

    const resp = await fetch(`/processos/${encodeURIComponent(numero)}`);
    if (!resp.ok) {
        alert('Não foi possível carregar o processo.');
        return;
    }
    const p = await resp.json();

    // Título / subtítulo
    document.getElementById('tituloProcesso').innerText = `Processo ${p.processo_numero}`;
    document.getElementById('subtituloProcesso').innerText = p.descricao || '';

    // Cards
    setText('det-numero', p.processo_numero);
    setText('det-data-criacao', formatDateBR(p.data_criacao));
    const situacaoSpan = document.getElementById('det-situacao');
    situacaoSpan.innerText = p.situacao;
    situacaoSpan.className = `status-pill status-${p.situacao}`;
    setText('det-unidade', p.unidade_atendida);
    setText('det-onde-esta', p.onde_esta);

    setText('det-valor', formatCurrencyBRL(Number(p.valor_previsto || 0)));
    setText('det-fonte', p.fonte_recurso);
    setText('det-modalidade', p.modalidade);
    setText('det-convenio', p.convenio);

    setText('det-gestor', p.gestor);
    setText('det-fiscal', p.fiscal);
    setText('det-instrucao', p.instrucao_responsavel);

    // Observações
    setText('det-observacao', p.observacao);
    setText('det-obs-adicionais', p.observacoes_adicionais);
    setText('det-obs-extras', p.obs_extras);

    // Timeline + Auditoria
    preencherTimeline(p);
    preencherAuditoria(p.auditorias || []);
}

window.addEventListener('DOMContentLoaded', () => {
    document.getElementById('btnVoltar').addEventListener('click', () => {
        window.history.back();
    });

    carregarDetalhes();
});
