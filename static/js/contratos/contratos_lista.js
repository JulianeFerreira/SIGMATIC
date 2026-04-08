function formatDateBR(value) {
    if (!value) return "";
    try {
        return new Date(value).toLocaleDateString("pt-BR");
    } catch (e) {
        return value;
    }
}

async function carregarContratos() {
    const categoria = document.getElementById("filtroCategoria").value;
    const empresa = document.getElementById("filtroEmpresa").value;
    const local = document.getElementById("filtroLocal").value;
    const statusVigencia = document.getElementById("filtroStatusVigencia").value;
    const statusTramitacao = document.getElementById("filtroStatusTramitacao").value;
    const busca = document.getElementById("filtroBuscaContrato").value;

    const params = new URLSearchParams();
    params.set("limit", "100");

    if (categoria) params.set("categoria_servico", categoria);
    if (empresa) params.set("empresa", empresa);
    if (local) params.set("local", local);
    if (statusVigencia) params.set("status_vigencia", statusVigencia);
    if (statusTramitacao) params.set("status_tramitacao", statusTramitacao);

    // Por enquanto, usamos a busca como filtro de empresa
    if (busca) params.set("empresa", busca);

    const resp = await fetch("/contratos?" + params.toString());
    const data = await resp.json();

    const tbody = document.getElementById("tabela-contratos-lista");
    tbody.innerHTML = "";

    document.getElementById("infoQuantidadeContratos").innerText =
        `Mostrando ${data.length} contrato(s)`;

    data.forEach(c => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${c.gms}</td>
            <td>${c.numero_contrato}</td>
            <td>${c.empresa}</td>
            <td>${c.categoria_servico}</td>
            <td>${c.local}</td>
            <td>${formatDateBR(c.data_inicio)}</td>
            <td>${formatDateBR(c.data_termino)}</td>
            <td>${c.status_vigencia || ""}</td>
            <td>${c.status_tramitacao || ""}</td>
            <td class="acoes-col">
                <button class="icon-btn" title="Ver detalhes">👁</button>
                <button class="icon-btn" title="Editar">✏️</button>
            </td>
        `;

        tbody.appendChild(tr);
    });
}

function configurarEventosContratos() {
    document.getElementById("btnNovoContrato").addEventListener("click", () => {
        window.location.href = "/ui/contratos/novo";
    });

    document.getElementById("btnExportarContratos").addEventListener("click", () => {
        alert("Exportação de contratos ainda não implementada.");
    });

    document.getElementById("filtroCategoria").addEventListener("change", carregarContratos);
    document.getElementById("filtroStatusVigencia").addEventListener("change", carregarContratos);
    document.getElementById("filtroStatusTramitacao").addEventListener("change", carregarContratos);
    document.getElementById("filtroEmpresa").addEventListener("keyup", () => {
        carregarContratos();
    });
    document.getElementById("filtroLocal").addEventListener("keyup", () => {
        carregarContratos();
    });
    document.getElementById("filtroBuscaContrato").addEventListener("keyup", () => {
        carregarContratos();
    });
}

window.addEventListener("DOMContentLoaded", () => {
    configurarEventosContratos();
    carregarContratos();
});
