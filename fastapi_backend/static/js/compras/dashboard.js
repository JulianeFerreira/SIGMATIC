function formatCurrencyBRL(value) {
    return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

async function carregarListaProcessos() {
    const busca = document.getElementById('filtroBusca').value;
    const situacao = document.getElementById('filtroSituacao').value;
    const modalidade = document.getElementById('filtroModalidade').value;

    const params = new URLSearchParams();
    params.set('limit', '50');
    if (busca) params.set('busca', busca);
    if (situacao) params.set('situacao', situacao);
    if (modalidade) params.set('modalidade', modalidade);

    const resp = await fetch('/processos?' + params.toString());
    const data = await resp.json();

    const tbody = document.getElementById('table-processos-lista');
    tbody.innerHTML = '';
    document.getElementById('infoQuantidade').innerText =
        `Mostrando ${data.length} processo(s)`;

    data.forEach(p => {
        const tr = document.createElement('tr');

        const valor = Number(p.valor_previsto || 0);
        const dataCriacao = p.data_criacao ? new Date(p.data_criacao).toLocaleDateString('pt-BR') : '';

        tr.innerHTML = `
            <td>${p.processo_numero}</td>
            <td>${p.descricao}</td>
            <td>${p.unidade_atendida || ''}</td>
            <td>${formatCurrencyBRL(valor)}</td>
            <td>${p.modalidade}</td>
            <td><span class="status-pill status-${p.situacao}">${p.situacao}</span></td>
            <td>${dataCriacao}</td>
            <td class="acoes-col">
                <button class="icon-btn" title="Ver detalhes">👁</button>
                <button class="icon-btn" title="Editar">✏️</button>
                <button class="icon-btn" title="Baixar">⬇️</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function configurarEventos() {
    document.getElementById('btnNovoProcesso').addEventListener('click', () => {
        window.location.href = '/ui/processos/novo';
    });

    document.getElementById('btnExportar').addEventListener('click', () => {
        window.location.href = '/relatorios/geral/export?formato=excel';
    });

    document.getElementById('filtroBusca').addEventListener('keyup', () => {
        carregarListaProcessos();
    });
    document.getElementById('filtroSituacao').addEventListener('change', carregarListaProcessos);
    document.getElementById('filtroModalidade').addEventListener('change', carregarListaProcessos);
}

window.addEventListener('DOMContentLoaded', () => {
    configurarEventos();
    carregarListaProcessos();
});
