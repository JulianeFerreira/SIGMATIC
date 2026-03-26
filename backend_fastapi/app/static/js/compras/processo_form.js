function buildProcessoPayload(formData) {
    const get = name => formData.get(name) || undefined;

    const payload = {
        processo_numero: get('processo_numero'),
        descricao: get('descricao'),
        unidade_atendida: get('unidade_atendida'),
        data_criacao: get('data_criacao'),
        valor_previsto: parseFloat(get('valor_previsto') || '0'),
        fonte_recurso: get('fonte_recurso'),
        modalidade: get('modalidade')
    };

    // opcionais
    const optionalFields = [
        'instrucao_responsavel',
        'convenio',
        'data_pregao',
        'prazo_entrega_dias',
        'data_prevista_entrega',
        'gestor',
        'fiscal',
        'situacao',
        'onde_esta',
        'observacao'
    ];

    optionalFields.forEach(f => {
        const v = get(f);
        if (v !== undefined && v !== '') {
            if (f === 'prazo_entrega_dias') {
                payload[f] = parseInt(v, 10);
            } else {
                payload[f] = v;
            }
        }
    });

    return payload;
}

window.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('processoForm');
    const btnCancelar = document.getElementById('btnCancelar');

    btnCancelar.addEventListener('click', () => {
        window.location.href = '/ui/processos';
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const payload = buildProcessoPayload(formData);

        try {
            const resp = await fetch('/processos', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!resp.ok) {
                const err = await resp.json().catch(() => ({}));
                alert('Erro ao salvar processo: ' + (err.detail || resp.statusText));
                return;
            }

            alert('Processo salvo com sucesso!');
            window.location.href = '/ui/processos';
        } catch (err) {
            console.error(err);
            alert('Erro de comunicação com o servidor.');
        }
    });
});
