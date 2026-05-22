let chartCategoria = null;
let chartTramitacao = null;

function escapeHTML(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}

function formatDateBR(value) {
    if (!value) return '';
    try {
        return new Date(value).toLocaleDateString('pt-BR');
    } catch {
        return value;
    }
}

async function apiGet(url) {
    const resp = await fetch(url);

    if (!resp.ok) {
        throw new Error(`Erro ao carregar: ${url}`);
    }

    return resp.json();
}

async function carregarDashboardContratos() {
    const data = await apiGet('/contratos/dashboard/metricas');

    document.getElementById('metric-total-contratos').innerText = data.total_contratos ?? 0;
    document.getElementById('metric-vigentes').innerText = data.vigentes ?? 0;
    document.getElementById('metric-proximo-venc').innerText = data.proximo_vencimento ?? 0;
    document.getElementById('metric-vencidos').innerText = data.vencidos ?? 0;
    document.getElementById('metric-prorrogados').innerText = data.prorrogados ?? 0;
    document.getElementById('metric-rescindidos').innerText = data.rescindidos ?? 0;

    montarGraficos(data);
    await carregarResumoContratos();
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
                    data: catValues
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

    if (ctxSt) {
        chartTramitacao = new Chart(ctxSt, {
            type: 'bar',
            data: {
                labels: stLabels,
                datasets: [{
                    data: stValues
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

async function carregarResumoContratos() {
    const tbody = document.getElementById('tabela-contratos-resumo');

    if (!tbody) return;

    tbody.innerHTML = `
        <tr>
            <td colspan="6" class="text-center text-muted">
                Carregando...
            </td>
        </tr>
    `;

    const data = await apiGet('/contratos_api?limit=8');
    const contratos = Array.isArray(data) ? data : [];

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
            <td><span class="status-pill">${escapeHTML(c.status_vigencia || '')}</span></td>
            <td><span class="status-pill">${escapeHTML(c.status_tramitacao || '')}</span></td>
        `;

        tbody.appendChild(tr);
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
