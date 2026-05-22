function buildProcessoPayload(formData) {
    const get = (name) => {
        const value = formData.get(name);
        return value === null || value === '' ? undefined : value;
    };

    const payload = {
        processo_numero: get('processo_numero'),
        descricao: get('descricao'),
        unidade_atendida: get('unidade_atendida'),
        data_criacao: get('data_criacao'),
        valor_previsto: Number(get('valor_previsto') || 0),
        fonte_recurso: get('fonte_recurso'),
        modalidade: get('modalidade'),
        situacao: get('situacao') || 'TRAMITANDO'
    };

    const optionalFields = [
        'instrucao_responsavel',
        'convenio',
        'data_pregao',
        'data_prevista_entrega',
        'gestor',
        'fiscal',
        'onde_esta',
        'observacao'
    ];

    optionalFields.forEach((field) => {
        const value = get(field);

        if (value !== undefined) {
            payload[field] = value;
        }
    });

    const prazoEntrega = get('prazo_entrega_dias');

    if (prazoEntrega !== undefined) {
        payload.prazo_entrega_dias = parseInt(prazoEntrega, 10);
    }

    return payload;
}

function validarProcesso(payload) {
    const obrigatorios = [
        { campo: 'processo_numero', label: 'Número do Processo' },
        { campo: 'descricao', label: 'Descrição' },
        { campo: 'unidade_atendida', label: 'Unidade Atendida' },
        { campo: 'data_criacao', label: 'Data de Criação' },
        { campo: 'valor_previsto', label: 'Valor Previsto' },
        { campo: 'fonte_recurso', label: 'Fonte do Recurso' },
        { campo: 'modalidade', label: 'Modalidade' }
    ];

    const faltando = obrigatorios.filter((item) => {
        const value = payload[item.campo];

        if (item.campo === 'valor_previsto') {
            return value === undefined || value === null || Number.isNaN(Number(value));
        }

        return value === undefined || value === null || value === '';
    });

    if (faltando.length) {
        alert('Preencha os campos obrigatórios: ' + faltando.map(f => f.label).join(', '));
        return false;
    }

    if (payload.prazo_entrega_dias !== undefined && Number.isNaN(payload.prazo_entrega_dias)) {
        alert('Prazo de entrega deve ser um número válido.');
        return false;
    }

    return true;
}

async function salvarProcesso(form) {
    const formData = new FormData(form);
    const payload = buildProcessoPayload(formData);

    if (!validarProcesso(payload)) {
        return;
    }

    try {
        const resp = await fetch('/processos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            alert('Erro ao salvar processo: ' + (err.detail || resp.statusText));
            return;
        }

        const data = await resp.json().catch(() => ({}));
        const numero = data.processo_numero || payload.processo_numero;

        alert('Processo salvo com sucesso!');
        window.location.href = `/ui/processos/${encodeURIComponent(numero)}/`;

    } catch (err) {
        console.error(err);
        alert('Erro de comunicação com o servidor.');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('processoForm');
    const btnCancelar = document.getElementById('btnCancelarProcesso') || document.getElementById('btnCancelar');

    btnCancelar?.addEventListener('click', () => {
        window.location.href = '/ui/processos/';
    });

    form?.addEventListener('submit', async (e) => {
        e.preventDefault();
        await salvarProcesso(form);
    });
});
