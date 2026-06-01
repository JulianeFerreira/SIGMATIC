let chartCategoria = null;
let chartTramitacao = null;
let chartVencimentos = null;

function escapeHTML(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}

function formatDateBR(value) {
    if (!value) return 'Não informado';

    try {
        return new Date(value).toLocaleDateString('pt-BR');
    } catch {
        return value;
    }
}

function formatCurrencyBR(value) {
    const numero = Number(value || 0);

    return numero.toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    });
}

async function apiGet(url) {
    const resp = await fetch(url);

    if (!resp.ok) {
        throw new Error(`Erro ao carregar: ${url}`);
    }

    return resp.json();
}

async function carregarDashboardContratos() {
    const metricas = await apiGet('/contratos/dashboard/metricas');

    document.getElementById('metric-total-contratos').innerText = metricas.total_contratos ?? 0;
    document.getElementById('metric-vigentes').innerText = metricas.vigentes ?? 0;
    document.getElementById('metric-proximo-venc').innerText = metricas.proximo_vencimento ?? 0;
    document.getElementById('metric-vencidos').innerText = metricas.vencidos ?? 0;
    document.getElementById('metric-prorrogados').innerText = metricas.prorrogados ?? 0;
    document.getElementById('metric-rescindidos').innerText = metricas.rescindidos ?? 0;

    montarGraficos(metricas);

    const dataContratos = await apiGet('/contratos_api?limit=100');
    const contratos = Array.isArray(dataContratos) ? dataContratos : [];

    carregarResumoContratos(contratos);
    carregarSemaforoContratos(contratos);
    carregarAlertasContratos(contratos);
    carregarValorTotal(contratos);
    carregarContratosPorFiscal(contratos);
    carregarTopFornecedores(contratos);
    montarGraficoVencimentos(contratos);
}

function montarGraficos(data) {
    const catLabels = (data.por_categoria || []).map(c => c.categoria || 'N/D');
    const catValues = (data.por_categoria || []).map(c => c.quantidade || 0);

    const stLabels = (data.por_status_tramitacao || []).map(s => s.status || 'N/D');
    const stValues = (data.por_status_tramitacao || []).map(s => s.quantidade || 0);

    const ctxCat = document.getElementById('chartContratosCategoria');
    const ctxSt = document.getElementById('chartContratosTramitacao');

    if (chartCategoria) chartCategoria.destroy();
    if (chartTramitacao) chartTramitacao.destroy();

    if (ctxCat) {
        chartCategoria = new Chart(ctxCat, {
            type: 'doughnut',
            data: {
                labels: catLabels,
                datasets: [{
                    data: catValues,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '62%',
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    if (ctxSt) {
        chartTramitacao = new Chart(ctxSt, {
            type: 'bar',
            data: {
                labels: stLabels,
                datasets: [{
                    data: stValues,
                    borderRadius: 8
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

function carregarResumoContratos(contratos) {
    const tbody = document.getElementById('tabela-contratos-resumo');

    if (!tbody) return;

    tbody.innerHTML = '';

    if (!contratos.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">
                    Nenhum contrato cadastrado.
                </td>
            </tr>
        `;
        return;
    }

    contratos.slice(0, 8).forEach(c => {
        const tr = document.createElement('tr');

        tr.innerHTML = `
            <td>${escapeHTML(c.gms)}</td>
            <td>${escapeHTML(c.numero_contrato)}</td>
            <td>${escapeHTML(c.empresa)}</td>
            <td>${escapeHTML(c.categoria_servico)}</td>
            <td><span class="badge bg-light text-dark border">${escapeHTML(c.status_vigencia || '')}</span></td>
            <td><span class="badge bg-light text-dark border">${escapeHTML(c.status_tramitacao || '')}</span></td>
        `;

        tbody.appendChild(tr);
    });
}

function carregarSemaforoContratos(contratos) {
    const tbody = document.getElementById('tabela-semaforo-contratos');

    if (!tbody) return;

    tbody.innerHTML = '';

    if (!contratos.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">
                    Nenhum contrato para análise.
                </td>
            </tr>
        `;
        return;
    }

    contratos.slice(0, 10).forEach(c => {
        const status = String(c.status_vigencia || '').toLowerCase();

        let cor = 'success';
        let texto = 'Regular';

        if (status.includes('vencido')) {
            cor = 'danger';
            texto = 'Vencido';
        } else if (status.includes('proximo') || status.includes('próximo')) {
            cor = 'warning';
            texto = 'Atenção';
        } else if (status.includes('rescindido')) {
            cor = 'secondary';
            texto = 'Rescindido';
        }

        const tr = document.createElement('tr');

        tr.innerHTML = `
            <td>${escapeHTML(c.numero_contrato)}</td>
            <td>${escapeHTML(c.empresa)}</td>
            <td>${escapeHTML(c.categoria_servico)}</td>
            <td>${formatDateBR(c.data_fim || c.vigencia_fim || c.data_vencimento)}</td>
            <td>${escapeHTML(c.status_vigencia || '')}</td>
            <td>
                <span class="badge bg-${cor}">
                    ${texto}
                </span>
            </td>
        `;

        tbody.appendChild(tr);
    });
}

function carregarAlertasContratos(contratos) {
    const container = document.getElementById('lista-alertas-contratos');
    const badge = document.getElementById('badge-alertas');

    if (!container) return;

    const alertas = contratos.filter(c => {
        const status = String(c.status_vigencia || '').toLowerCase();
        const tramite = String(c.status_tramitacao || '').toLowerCase();

        return status.includes('vencido') ||
               status.includes('proximo') ||
               status.includes('próximo') ||
               tramite.includes('prorrogacao') ||
               tramite.includes('prorrogação') ||
               tramite.includes('aditivo');
    });

    badge.innerText = alertas.length;

    if (!alertas.length) {
        container.innerHTML = `
            <div class="alert alert-success mb-0">
                Nenhuma pendência crítica identificada.
            </div>
        `;
        return;
    }

    container.innerHTML = alertas.slice(0, 5).map(c => {
        const status = String(c.status_vigencia || '').toLowerCase();

        let classe = 'warning';
        let titulo = 'Atenção';

        if (status.includes('vencido')) {
            classe = 'danger';
            titulo = 'Crítico';
        }

        return `
            <div class="alert alert-${classe} mb-0 py-2">
                <div class="fw-bold">
                    ${escapeHTML(c.numero_contrato)} - ${escapeHTML(c.empresa)}
                </div>
                <small>
                    ${titulo}: ${escapeHTML(c.status_vigencia || c.status_tramitacao || 'Verificar contrato')}
                </small>
            </div>
        `;
    }).join('');
}

function carregarValorTotal(contratos) {
    const el = document.getElementById('metric-valor-total');

    if (!el) return;

    const total = contratos.reduce((acc, c) => {
        return acc + Number(c.valor_total || c.valor || c.valor_contrato || 0);
    }, 0);

    el.innerText = formatCurrencyBR(total);
}

function carregarContratosPorFiscal(contratos) {
    const container = document.getElementById('lista-fiscais');

    if (!container) return;

    const mapa = {};

    contratos.forEach(c => {
        const fiscal = c.fiscal || c.fiscal_contrato || 'Não informado';
        mapa[fiscal] = (mapa[fiscal] || 0) + 1;
    });

    const linhas = Object.entries(mapa)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 6);

    if (!linhas.length) {
        container.innerHTML = `<div class="text-muted">Nenhum fiscal informado.</div>`;
        return;
    }

    container.innerHTML = `
        <table class="table table-sm align-middle mb-0">
            <thead>
                <tr>
                    <th>Fiscal</th>
                    <th class="text-end">Contratos</th>
                </tr>
            </thead>
            <tbody>
                ${linhas.map(([fiscal, total]) => `
                    <tr>
                        <td>${escapeHTML(fiscal)}</td>
                        <td class="text-end fw-bold">${total}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function carregarTopFornecedores(contratos) {
    const container = document.getElementById('lista-fornecedores');

    if (!container) return;

    const mapa = {};

    contratos.forEach(c => {
        const fornecedor = c.empresa || 'Não informado';
        const valor = Number(c.valor_total || c.valor || c.valor_contrato || 0);

        if (!mapa[fornecedor]) {
            mapa[fornecedor] = {
                quantidade: 0,
                valor: 0
            };
        }

        mapa[fornecedor].quantidade += 1;
        mapa[fornecedor].valor += valor;
    });

    const linhas = Object.entries(mapa)
        .sort((a, b) => b[1].valor - a[1].valor)
        .slice(0, 6);

    if (!linhas.length) {
        container.innerHTML = `<div class="text-muted">Nenhum fornecedor informado.</div>`;
        return;
    }

    container.innerHTML = `
        <table class="table table-sm align-middle mb-0">
            <thead>
                <tr>
                    <th>Fornecedor</th>
                    <th class="text-end">Qtd.</th>
                    <th class="text-end">Valor</th>
                </tr>
            </thead>
            <tbody>
                ${linhas.map(([fornecedor, dados]) => `
                    <tr>
                        <td>${escapeHTML(fornecedor)}</td>
                        <td class="text-end">${dados.quantidade}</td>
                        <td class="text-end fw-bold">${formatCurrencyBR(dados.valor)}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function montarGraficoVencimentos(contratos) {
    const ctx = document.getElementById('chartContratosVencimentos');

    if (!ctx) return;

    const mapa = {};

    contratos.forEach(c => {
        const data = c.data_fim || c.vigencia_fim || c.data_vencimento;

        if (!data) return;

        const d = new Date(data);

        if (isNaN(d)) return;

        const chave = d.toLocaleDateString('pt-BR', {
            month: 'short',
            year: 'numeric'
        });

        mapa[chave] = (mapa[chave] || 0) + 1;
    });

    const labels = Object.keys(mapa);
    const valores = Object.values(mapa);

    if (chartVencimentos) chartVencimentos.destroy();

    chartVencimentos = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                data: valores,
                borderRadius: 8
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    carregarDashboardContratos().catch(err => {
        console.error(err);

        const tbody = document.getElementById('tabela-contratos-resumo');

        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-danger">
                        Erro ao carregar dashboard de contratos.
                    </td>
                </tr>
            `;
        }
    });
});
