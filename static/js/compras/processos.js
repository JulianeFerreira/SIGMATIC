function formatCurrencyBRL(value) {
    return Number(value || 0).toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    });
}

function formatDateBR(value) {
    if (!value) return '';
    try {
        return new Date(value).toLocaleDateString('pt-BR');
    } catch {
        return value;
    }
}

function escapeHTML(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}

async function carregarListaProcessos() {
    const busca = document.getElementById('filtroBusca')?.value || '';
    const situacao = document.getElementById('filtroSituacao')?.value || '';
    const modalidade = document.getElementById('filtroModalidade')?.value || '';

    const params = new URLSearchParams();
    params.set('limit', '100');

    if (busca) params.set('busca', busca);
    if (situacao) params.set('situacao', situacao);
    if (modalidade) params.set('modalidade', modalidade);

    const resp = await fetch('/processos?' + params.toString());

    if (!resp.ok) {
        throw new Error('Erro ao carregar processos.');
    }

    const data = await resp.json();
    const processos = Array.isArray(data) ? data : [];

    const tbody = document.getElementById('table-processos-lista');
    const info = document.getElementById('infoQuantidade');

    if (!tbody) return;

    tbody.innerHTML = '';

    if (info) {
        info.innerText = `Mostrando ${processos.length} processo(s)`;
    }

    if (!processos.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-muted">
                    Nenhum processo encontrado.
                </td>
            </tr>
        `;
        return;
    }

    processos.forEach(p => {
        const tr = document.createElement('tr');

        const numero = escapeHTML(p.processo_numero);
        const descricao = escapeHTML(p.descricao);
        const unidade = escapeHTML(p.unidade_atendida || '');
        const modalidadeTexto = escapeHTML(p.modalidade || '');
        const situacaoTexto = escapeHTML(p.situacao || '');
        const dataCriacao = formatDateBR(p.data_criacao);

        tr.innerHTML = `
            <td>
                <a href="/ui/processos/${encodeURIComponent(p.processo_numero)}/">
                    ${numero}
                </a>
            </td>
            <td>${descricao}</td>
            <td>${unidade}</td>
            <td>${formatCurrencyBRL(p.valor_previsto)}</td>
            <td>${modalidadeTexto}</td>
            <td>
                <span class="status-pill status-${situacaoTexto}">
                    ${situacaoTexto}
                </span>
            </td>
            <td>${dataCriacao}</td>
            <td class="acoes-col">
                <a class="btn secondary btn-sm"
                   href="/ui/processos/${encodeURIComponent(p.processo_numero)}/">
                    Ver
                </a>
            </td>
        `;

        tbody.appendChild(tr);
    });
}

function configurarEventos() {
    document.getElementById('btnNovoProcesso')?.addEventListener('click', () => {
        window.location.href = '/ui/processos/novo/';
    });

    document.getElementById('btnExportar')?.addEventListener('click', () => {
        window.location.href = '/ui/relatorios/';
    });

    document.getElementById('searchInputProcessos')?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            document.getElementById('filtroBusca').value = e.target.value || '';
            carregarListaProcessos();
        }
    });

    document.getElementById('filtroBusca')?.addEventListener('input', carregarListaProcessos);
    document.getElementById('filtroSituacao')?.addEventListener('change', carregarListaProcessos);
    document.getElementById('filtroModalidade')?.addEventListener('change', carregarListaProcessos);
}

document.addEventListener('DOMContentLoaded', () => {
    configurarEventos();

    carregarListaProcessos().catch(err => {
        console.error(err);

        const tbody = document.getElementById('table-processos-lista');

        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center text-danger">
                        Erro ao carregar processos.
                    </td>
                </tr>
            `;
        }
    });
});
