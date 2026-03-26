function formatDateBR(value) {
    if (!value) return "";
    try {
        return new Date(value).toLocaleDateString("pt-BR");
    } catch (e) {
        return value;
    }
}

async function carregarEstatisticasRapidasContratos() {
    const resp = await fetch("/contratos/dashboard/metricas");
    const data = await resp.json();

    document.getElementById("qs-total-contratos").innerText = data.total_contratos || 0;
    document.getElementById("qs-vigentes").innerText = data.vigentes || 0;
    document.getElementById("qs-prox-venc").innerText = data.proximo_vencimento || 0;
    document.getElementById("qs-vencidos").innerText = data.vencidos || 0;
}

async function carregarContratosBase() {
    const resp = await fetch("/contratos?limit=500");
    const data = await resp.json();
    return Array.isArray(data) ? data : [];
}

function aplicarFiltrosBasicos(lista, tipo) {
    const categoria = document.getElementById("filtroCategoriaRel").value;
    const empresa = document.getElementById("filtroEmpresaRel").value.trim().toLowerCase();
    const statusVig = document.getElementById("filtroStatusVigRel").value;
    const statusTram = document.getElementById("filtroStatusTramRel").value;
    const inicio = document.getElementById("filtroPeriodoInicioContrato").value;
    const fim = document.getElementById("filtroPeriodoFimContrato").value;

    return lista.filter(c => {
        if (categoria && c.categoria_servico !== categoria) return false;
        if (empresa && !(c.empresa || "").toLowerCase().includes(empresa)) return false;
        if (statusVig && c.status_vigencia !== statusVig) return false;
        if (statusTram && c.status_tramitacao !== statusTram) return false;

        if (inicio) {
            if (!c.data_inicio) return false;
            if (new Date(c.data_inicio) < new Date(inicio)) return false;
        }
        if (fim) {
            if (!c.data_termino) return false;
            if (new Date(c.data_termino) > new Date(fim)) return false;
        }

        if (tipo === "vencimentos") {
            const s = c.status_vigencia || "";
            if (!(s === "vencido" || s === "proximo_vencimento")) return false;
        }

        if (tipo === "tramitacao") {
            if (!c.status_tramitacao) return false;
        }

        return true;
    });
}

function preencherTabelaRelatorios(lista) {
    const tbody = document.getElementById("tabela-relatorios-contratos");
    tbody.innerHTML = "";

    if (!lista.length) {
        const tr = document.createElement("tr");
        const td = document.createElement("td");
        td.colSpan = 9;
        td.textContent = "Nenhum contrato encontrado para os critérios selecionados.";
        tbody.appendChild(tr);
        tr.appendChild(td);
        return;
    }

    lista.forEach(c => {
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
        `;
        document.getElementById("tabela-relatorios-contratos").appendChild(tr);
    });
}

async function gerarRelatorio(tipo) {
    const base = await carregarContratosBase();
    const filtrados = aplicarFiltrosBasicos(base, tipo);
    preencherTabelaRelatorios(filtrados);
}

function configurarEventosRelatoriosContratos() {
    document.getElementById("btnRelVencimentos").addEventListener("click", (e) => {
        e.preventDefault();
        gerarRelatorio("vencimentos");
    });

    document.getElementById("btnRelCategoria").addEventListener("click", (e) => {
        e.preventDefault();
        gerarRelatorio("categoria");
    });

    document.getElementById("btnRelEmpresa").addEventListener("click", (e) => {
        e.preventDefault();
        gerarRelatorio("empresa");
    });

    document.getElementById("btnRelTramitacao").addEventListener("click", (e) => {
        e.preventDefault();
        gerarRelatorio("tramitacao");
    });

    document.getElementById("btnGerarRelatorioPersonalizado").addEventListener("click", (e) => {
        e.preventDefault();
        gerarRelatorio("personalizado");
    });
}

window.addEventListener("DOMContentLoaded", () => {
    configurarEventosRelatoriosContratos();
    carregarEstatisticasRapidasContratos();
    // Opcional: já carregar algo ao abrir (por exemplo, todos)
    // gerarRelatorio("personalizado");
});
