function configurarBotoesRelatorios() {
    document.getElementById('btnRelGeral').addEventListener('click', () => {
        window.location.href = '/relatorios/geral/export?formato=excel';
    });

    document.getElementById('btnRelAtraso').addEventListener('click', () => {
        window.location.href = '/relatorios/atraso/export?formato=excel';
    });

    // por enquanto usamos o mesmo geral/export como stub
    document.getElementById('btnRelFinanceiro').addEventListener('click', () => {
        window.location.href = '/relatorios/geral/export?formato=excel';
    });

    document.getElementById('btnRelGestor').addEventListener('click', () => {
        window.location.href = '/relatorios/geral/export?formato=excel';
    });

    document.getElementById('btnRelPersonalizado').addEventListener('click', () => {
        const inicio = document.getElementById('filtroPeriodoInicio').value;
        const fim = document.getElementById('filtroPeriodoFim').value;
        const situacao = document.getElementById('filtroRelSituacao').value;
        const modalidade = document.getElementById('filtroRelModalidade').value;
        const unidade = document.getElementById('filtroRelUnidade').value;
        const formato = document.getElementById('filtroRelFormato').value;

        const params = new URLSearchParams();
        params.set('formato', formato || 'excel');
        if (inicio) params.set('data_inicio', inicio);
        if (fim) params.set('data_fim', fim);
        if (situacao) params.set('situacao', situacao);
        if (modalidade) params.set('modalidade', modalidade);
        if (unidade) params.set('unidade_atendida', unidade);

        // backend atual ainda não usa todos os filtros,
        // mas já deixamos preparado
        window.location.href = '/relatorios/geral/export?' + params.toString();
    });
}

async function carregarQuickStats() {
    const resp = await fetch('/dashboard/metricas');
    const data = await resp.json();

    document.getElementById('qs-total').innerText = data.total_processos;
    document.getElementById('qs-finalizados').innerText = data.processos_finalizados;
    document.getElementById('qs-tramitando').innerText = data.processos_tramitando;
    document.getElementById('qs-atrasados').innerText = data.processos_atrasados;
}

window.addEventListener('DOMContentLoaded', () => {
    configurarBotoesRelatorios();
    carregarQuickStats();
});
