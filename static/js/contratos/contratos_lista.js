function formatDateBR(value) {
    if (!value) return "";
    try {
        return new Date(value).toLocaleDateString("pt-BR");
    } catch {
        return value;
    }
}

function escapeHTML(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

async function carregarContratos() {
    const categoria = document.getElementById("filtroCategoria")?.value || "";
    const empresa = document.getElementById("filtroEmpresa")?.value || "";
    const local = document.getElementById("filtroLocal")?.value || "";
    const statusVigencia = document.getElementById("filtroStatusVigencia")?.value || "";
    const statusTramitacao = document.getElementById("filtroStatusTramitacao")?.value || "";
    const busca = document.getElementById("filtroBuscaContrato")?.value || "";

    const params = new URLSearchParams();
    params.set("limit", "100");

    if (categoria) params.set("categoria_servico", categoria);
    if (empresa) params.set("empresa", empresa);
    if (local) params.set("local", local);
    if (statusVigencia) params.set("status_vigencia", statusVigencia);
    if (statusTramitacao) params.set("status_tramitacao", statusTramitacao);

    if (busca) {
        params.set("busca", busca);
    }

    const resp = await fetch("/contratos_api?" + params.toString());

    if (!resp.ok) {
        throw new Error("Erro ao carregar contratos.");
    }

    const data = await resp.json();
    const contratos = Array.isArray(data) ? data : [];

    const tbody = document.getElementById("tabela-contratos-lista");
    const info = document.getElementById("infoQuantidadeContratos");

    if (!tbody) return;

    tbody.innerHTML = "";

    if (info) {
        info.innerText = `Mostrando ${contratos.length} contrato(s)`;
    }

    if (!contratos.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="10" class="text-center text-muted">
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
            <td><span class="status-pill">${escapeHTML(c.status_vigencia || "")}</span></td>
            <td><span class="status-pill">${escapeHTML(c.status_tramitacao || "")}</span></td>
            <td class="acoes-col">
                <button class="btn secondary btn-sm" type="button" title="Ver detalhes">
                    Ver
                </button>
            </td>
        `;

        tbody.appendChild(tr);
    });
}

function configurarEventosContratos() {
    document.getElementById("btnNovoContrato")?.addEventListener("click", () => {
        window.location.href = "/ui/contratos/novo/";
    });

    document.getElementById("btnExportarContratos")?.addEventListener("click", () => {
        alert("Exportação de contratos ainda não implementada.");
    });

    document.getElementById("filtroCategoria")?.addEventListener("change", carregarContratos);
    document.getElementById("filtroStatusVigencia")?.addEventListener("change", carregarContratos);
    document.getElementById("filtroStatusTramitacao")?.addEventListener("change", carregarContratos);
    document.getElementById("filtroEmpresa")?.addEventListener("input", carregarContratos);
    document.getElementById("filtroLocal")?.addEventListener("input", carregarContratos);
    document.getElementById("filtroBuscaContrato")?.addEventListener("input", carregarContratos);
}

document.addEventListener("DOMContentLoaded", () => {
    configurarEventosContratos();

    carregarContratos().catch(err => {
        console.error(err);

        const tbody = document.getElementById("tabela-contratos-lista");

        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="10" class="text-center text-danger">
                        Erro ao carregar contratos.
                    </td>
                </tr>
            `;
        }
    });
});
