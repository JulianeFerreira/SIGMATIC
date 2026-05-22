function escapeHTML(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function formatDateBR(value) {
    if (!value) return "";

    try {
        return new Date(value).toLocaleDateString("pt-BR");
    } catch {
        return value;
    }
}

async function carregarQuickStatsContratos() {
    const resp = await fetch("/contratos/dashboard/metricas");

    if (!resp.ok) {
        throw new Error("Erro ao carregar métricas.");
    }

    const data = await resp.json();

    document.getElementById("qs-total-contratos").innerText =
        data.total_contratos ?? 0;

    document.getElementById("qs-vigentes").innerText =
        data.vigentes ?? 0;

    document.getElementById("qs-prox-venc").innerText =
        data.proximo_vencimento ?? 0;

    document.getElementById("qs-vencidos").innerText =
        data.vencidos ?? 0;
}

async function gerarRelatorioPersonalizado() {
    const categoria =
        document.getElementById("filtroCategoriaRel")?.value || "";

    const empresa =
        document.getElementById("filtroEmpresaRel")?.value || "";

    const statusVig =
        document.getElementById("filtroStatusVigRel")?.value || "";

    const statusTram =
        document.getElementById("filtroStatusTramRel")?.value || "";

    const inicio =
        document.getElementById("filtroPeriodoInicioContrato")?.value || "";

    const fim =
        document.getElementById("filtroPeriodoFimContrato")?.value || "";

    const params = new URLSearchParams();
    params.set("limit", "200");

    if (categoria) params.set("categoria_servico", categoria);
    if (empresa) params.set("empresa", empresa);
    if (statusVig) params.set("status_vigencia", statusVig);
    if (statusTram) params.set("status_tramitacao", statusTram);
    if (inicio) params.set("data_inicio", inicio);
    if (fim) params.set("data_fim", fim);

    const resp = await fetch("/contratos_api?" + params.toString());

    if (!resp.ok) {
        throw new Error("Erro ao gerar relatório.");
    }

    const data = await resp.json();
    preencherTabelaRelatorio(data);
}

function preencherTabelaRelatorio(contratos) {
    const tbody = document.getElementById("tabela-relatorios-contratos");

    if (!tbody) return;

    tbody.innerHTML = "";

    if (!contratos || !contratos.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-muted">
                    Nenhum contrato encontrado.
                </td>
            </tr>
        `;
        return;
    }

    contratos.forEach(c => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${escapeHTML(c.gms)}</td>
            <td>${escapeHTML(c.numero_contrato)}</td>
            <td>${escapeHTML(c.empresa)}</td>
            <td>${escapeHTML(c.categoria_servico)}</td>
            <td>${escapeHTML(c.local)}</td>
            <td>${formatDateBR(c.data_inicio)}</td>
            <td>${formatDateBR(c.data_termino)}</td>
            <td>
                <span class="status-pill">
                    ${escapeHTML(c.status_vigencia || "")}
                </span>
            </td>
            <td>
                <span class="status-pill">
                    ${escapeHTML(c.status_tramitacao || "")}
                </span>
            </td>
        `;

        tbody.appendChild(tr);
    });
}

function configurarEventosRelatoriosContratos() {

    document.getElementById("btnRelVencimentos")
        ?.addEventListener("click", async () => {

            document.getElementById("filtroStatusVigRel").value =
                "proximo_vencimento";

            await gerarRelatorioPersonalizado();
        });

    document.getElementById("btnRelCategoria")
        ?.addEventListener("click", async () => {
            await gerarRelatorioPersonalizado();
        });

    document.getElementById("btnRelEmpresa")
        ?.addEventListener("click", async () => {
            await gerarRelatorioPersonalizado();
        });

    document.getElementById("btnRelTramitacao")
        ?.addEventListener("click", async () => {
            await gerarRelatorioPersonalizado();
        });

    document.getElementById("btnGerarRelatorioPersonalizado")
        ?.addEventListener("click", async () => {

            try {
                await gerarRelatorioPersonalizado();
            } catch (err) {
                console.error(err);
                alert("Erro ao gerar relatório.");
            }
        });
}

document.addEventListener("DOMContentLoaded", () => {

    configurarEventosRelatoriosContratos();

    carregarQuickStatsContratos().catch(err => {
        console.error(err);
    });

});
