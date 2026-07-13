let chartCategoria = null;
let chartTramitacao = null;

async function carregarDashboardContratos() {
    const resp = await fetch("/contratos/dashboard/metricas");
    const data = await resp.json();

    // Métricas numéricas
    document.getElementById("metric-total-contratos").innerText = data.total_contratos || 0;
    document.getElementById("metric-vigentes").innerText = data.vigentes || 0;
    document.getElementById("metric-proximo-venc").innerText = data.proximo_vencimento || 0;
    document.getElementById("metric-vencidos").innerText = data.vencidos || 0;
    document.getElementById("metric-prorrogados").innerText = data.prorrogados || 0;
    document.getElementById("metric-rescindidos").innerText = data.rescindidos || 0;

    // Gráfico por categoria
    const catLabels = (data.por_categoria || []).map(c => c.categoria || "N/D");
    const catValues = (data.por_categoria || []).map(c => c.quantidade || 0);

    const ctxCat = document.getElementById("chartContratosCategoria").getContext("2d");
    if (chartCategoria) chartCategoria.destroy();
    chartCategoria = new Chart(ctxCat, {
        type: "pie",
        data: {
            labels: catLabels,
            datasets: [{
                data: catValues
            }]
        }
    });

    // Gráfico por status de tramitação
    const stLabels = (data.por_status_tramitacao || []).map(s => s.status || "N/D");
    const stValues = (data.por_status_tramitacao || []).map(s => s.quantidade || 0);

    const ctxSt = document.getElementById("chartContratosTramitacao").getContext("2d");
    if (chartTramitacao) chartTramitacao.destroy();
    chartTramitacao = new Chart(ctxSt, {
        type: "bar",
        data: {
            labels: stLabels,
            datasets: [{
                data: stValues
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { precision: 0 }
                }
            }
        }
    });
}

window.addEventListener("DOMContentLoaded", () => {
    carregarDashboardContratos();
});
