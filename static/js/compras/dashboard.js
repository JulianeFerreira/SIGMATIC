let chartModalidade = null;
let chartSituacao = null;
let processosDashboard = [];

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

function countBy(lista, campo) {
    const mapa = {};

    lista.forEach(item => {
        const chave = item[campo] || 'Não informado';
        mapa[chave] = (mapa[chave] || 0) + 1;
    });

    return mapa;
}

function processoAtrasado(processo) {
    if (!processo.data_prevista_entrega) return false;

    const situacao = String(processo.situacao || '').toUpperCase();

    if (situacao === 'FINALIZADO' || situacao === 'ARQUIVADO') {
        return false;
    }

    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);

    const prazo = new Date(processo.data_prevista_entrega);
    prazo.setHours(0, 0, 0, 0);

    return prazo < hoje;
}

async function carregarProcessosDashboard() {
    const resp = await fetch('/processos?limit=500');

    if (!resp.ok) {
        throw new Error('Erro ao carregar processos.');
    }

    const data = await resp.json();
    processosDashboard = Array.isArray(data) ? data : [];

    atualizarMetricas(processosDashboard);
    atualizarGraficos(processosDashboard);
    atualizarTabela(processosDashboard);
}

function atualizarMetricas(processos) {
    const total = processos.length;

    const valorTotal = processos.reduce((acc, p) => {
        return acc + Number(p.valor_previsto || 0);
    }, 0);

    const finalizados = processos.filter(p => String(p.situacao || '').toUpperCase() === 'FINALIZADO').length;
    const tramitando = processos.filter(p => String(p.situacao || '').toUpperCase() === 'TRAMITANDO').length;
    const arquivados = processos.filter(p => String(p.situacao || '').toUpperCase() === 'ARQUIVADO').length;
    const atrasados = processos.filter(processoAtrasado).length;

    document.getElementById('metric-total').innerText = total;
    document.getElementById('metric-valor').innerText = formatCurrencyBRL(valorTotal);
    document.getElementById('metric-finalizados').innerText = finalizados;
    document.getElementById('metric-tramitando').innerText = tramitando;
    document.getElementById('metric-arquivados').innerText = arquivados;
    document.getElementById('metric-atrasados').innerText = atrasados;
}

function atualizarGraficos(processos) {
    const porModalidade = countBy(processos, 'modalidade');
    const porSituacao = countBy(processos, 'situacao');

    const modalidadeLabels = Object.keys(porModalidade);
    const modalidadeValues = modalidadeLabels.map(label => porModalidade[label]);

    const situacaoLabels = Object.keys(porSituacao);
    const situacaoValues = situacaoLabels.map(label => porSituacao[label]);

    const ctxModalidade = document.getElementById('chartModalidade');
    const ctxSituacao = document.getElementById('chartSituacao');

    if (chartModalidade) chartModalidade.destroy();
    if (chartSituacao) chartSituacao.destroy();

    if (ctxModalidade) {
        chartModalidade = new Chart(ctxModalidade, {
            type: 'doughnut',
            data: {
                labels: modalidadeLabels,
                datasets: [{
                    data: modalidadeValues
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    if (ctxSituacao) {
        chartSituacao = new Chart(ctxSituacao, {
            type: 'bar',
            data: {
                labels: situacaoLabels,
                datasets: [{
                    data: situacaoValues
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }
}

function atualizarTabela(processos) {
    const tbody = document.getElementById('table-processos');

    if (!tbody) return;

    tbody.innerHTML = '';

    const lista = processos.slice(0, 12);

    if (!lista.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-muted">
                    Nenhum processo encontrado.
                </td>
            </tr>
        `;
        return;
    }

    lista.forEach(p => {
        const tr = document.createElement('tr');

        const numero = escapeHTML(p.processo_numero);
        const descricao = escapeHTML(p.descricao);
        const unidade = escapeHTML(p.unidade_atendida || '');
        const modalidade = escapeHTML(p.modalidade || '');
        const situacao = escapeHTML(p.situacao || '');
        const dataCriacao = formatDateBR(p.data_criacao);

        tr.innerHTML = `
            <td>
                <a href="/ui/processos/${encodeURIComponent(p.processo_numero)}/">
                    ${numero}
                </a>
            </td>
            <td>${descricao}</td>
            <td>${unidade}</td>
            <td>${formatCurrencyBRL(p.valor_previsto)}</td>
            <td>${modalidade}</td>
            <td>
                <span class="status-pill status-${situacao}">
                    ${situacao}
                </span>
            </td>
            <td>${dataCriacao}</td>
        `;

        tbody.appendChild(tr);
    });
}

function filtrarDashboard(termo) {
    const busca = String(termo || '').trim().toLowerCase();

    if (!busca) {
        atualizarTabela(processosDashboard);
        return;
    }

    const filtrados = processosDashboard.filter(p => {
        return [
            p.processo_numero,
            p.descricao,
            p.unidade_atendida,
            p.modalidade,
            p.situacao
        ].some(campo => String(campo || '').toLowerCase().includes(busca));
    });

    atualizarTabela(filtrados);
}

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');

    searchInput?.addEventListener('keyup', (e) => {
        filtrarDashboard(e.target.value);
    });

    carregarProcessosDashboard().catch(err => {
        console.error(err);

        const tbody = document.getElementById('table-processos');

        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-danger">
                        Erro ao carregar dashboard.
                    </td>
                </tr>
            `;
        }
    });
});
