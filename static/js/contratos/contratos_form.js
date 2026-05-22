function coletarDadosContrato() {
    return {
        gms: document.getElementById("gms")?.value.trim(),
        numero_contrato: document.getElementById("numero_contrato")?.value.trim(),
        empresa: document.getElementById("empresa")?.value.trim(),
        categoria_servico: document.getElementById("categoria_servico")?.value,
        local: document.getElementById("local")?.value.trim(),
        quantidade: document.getElementById("quantidade")?.value.trim() || null,
        posto: document.getElementById("posto")?.value.trim() || null,

        data_inicio: document.getElementById("data_inicio")?.value || null,
        data_termino: document.getElementById("data_termino")?.value || null,

        status_vigencia: document.getElementById("status_vigencia")?.value || null,
        status_tramitacao: document.getElementById("status_tramitacao")?.value || null,
        status_financeiro: document.getElementById("status_financeiro")?.value || null,

        status_ta: document.getElementById("status_ta")?.value || null,
        observacoes_ta: document.getElementById("observacoes_ta")?.value.trim() || null,

        status_tap: document.getElementById("status_tap")?.value || null,
        ano_reajuste: document.getElementById("ano_reajuste")?.value.trim() || null,

        numero_protocolo: document.getElementById("numero_protocolo")?.value.trim() || null,
        descricao_tramitacao: document.getElementById("descricao_tramitacao")?.value.trim() || null,
        localizacao_documento: document.getElementById("localizacao_documento")?.value.trim() || null,
        data_tramitacao: document.getElementById("data_tramitacao")?.value || null,

        observacoes_gerais: document.getElementById("observacoes_gerais")?.value.trim() || null,
        historico_alteracoes: document.getElementById("historico_alteracoes")?.value.trim() || null
    };
}

function validarContrato(dados) {
    const obrigatorios = [
        { campo: "gms", label: "Número GMS" },
        { campo: "numero_contrato", label: "Número do Contrato" },
        { campo: "empresa", label: "Empresa" },
        { campo: "categoria_servico", label: "Categoria do Serviço" },
        { campo: "local", label: "Local" },
        { campo: "data_inicio", label: "Data de Início" },
        { campo: "data_termino", label: "Data de Término" }
    ];

    const faltando = obrigatorios.filter(item => !dados[item.campo]);

    if (faltando.length > 0) {
        alert("Preencha os campos obrigatórios: " + faltando.map(f => f.label).join(", "));
        return false;
    }

    const dataInicio = new Date(dados.data_inicio);
    const dataTermino = new Date(dados.data_termino);

    if (dataTermino < dataInicio) {
        alert("A data de término não pode ser anterior à data de início.");
        return false;
    }

    return true;
}

async function salvarContrato() {
    const dados = coletarDadosContrato();

    if (!validarContrato(dados)) {
        return;
    }

    try {
        const resp = await fetch("/contratos_api", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(dados)
        });

        if (!resp.ok) {
            const erro = await resp.json().catch(() => ({}));
            alert("Erro ao salvar contrato: " + (erro.detail || resp.statusText));
            return;
        }

        alert("Contrato salvo com sucesso!");
        window.location.href = "/ui/contratos/lista/";

    } catch (e) {
        console.error(e);
        alert("Erro de comunicação com o servidor.");
    }
}

function configurarEventosContratoForm() {
    document.getElementById("btnSalvarContrato")?.addEventListener("click", (e) => {
        e.preventDefault();
        salvarContrato();
    });

    document.getElementById("btnCancelarContrato")?.addEventListener("click", (e) => {
        e.preventDefault();
        window.location.href = "/ui/contratos/lista/";
    });
}

document.addEventListener("DOMContentLoaded", () => {
    configurarEventosContratoForm();
});
