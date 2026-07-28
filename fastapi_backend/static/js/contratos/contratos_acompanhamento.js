document.addEventListener('DOMContentLoaded', function() {
    console.log('Acompanhamento Conectado ao Banco de Dados Local SQLite.');

    // 1. Controle de alternância das Sub-Abas internas (Itens / Histórico)
    const subTabButtons = document.querySelectorAll('.sub-tab-btn');
    const subTabPanes = document.querySelectorAll('.sub-tab-pane');

    subTabButtons.forEach(button => {
        button.addEventListener('click', function() {
            subTabButtons.forEach(btn => { 
                btn.classList.remove('active', 'btn-primary'); 
                btn.classList.add('btn-light'); 
            });
            this.classList.remove('btn-light'); 
            this.classList.add('active', 'btn-primary');
            
            subTabPanes.forEach(pane => pane.classList.add('d-none'));
            const targetId = this.getAttribute('data-target');
            if (document.getElementById(targetId)) {
                document.getElementById(targetId).classList.remove('d-none');
            }
        });
    });

    // 2. FUNÇÃO ISOLADA DE BUSCA (Para poder ser chamada pelo Enter ou pela URL)
    function buscarContrato(termoBusca) {
        if (!termoBusca) return;

        console.log(`A procurar o contrato "${termoBusca}" no banco de dados local...`);

        fetch(`/api/buscar-contrato/?q=${encodeURIComponent(termoBusca)}`)
            .then(response => {
                if (!response.ok) throw new Error('Contrato não encontrado no banco de dados local.');
                return response.json();
            })
            .then(contrato => {
                carregarDadosNaTela(contrato);
            })
            .catch(error => {
                alert(error.message + " Verifique se o número foi digitado corretamente.");
                console.error(error);
            });
    }

    // 3. Escuta o campo de busca superior (Busca Manual por Enter)
    const campoBusca = document.getElementById('filtroAcompanhamentoContrato');
    if (campoBusca) {
        campoBusca.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                buscarContrato(this.value.trim());
            }
        });
    }

    // 4. VERIFICA SE VEIO CONTRATO VIA URL
    const urlParams = new URLSearchParams(window.location.search);
    const contratoParam = urlParams.get('q');
    if (contratoParam) {
        if (campoBusca) campoBusca.value = contratoParam; // Coloca o número no input
        buscarContrato(contratoParam);                    // Dispara a busca automática
    }

    // 5. Função responsável por distribuir os dados recebidos do banco nos elementos HTML
    function carregarDadosNaTela(contrato) {
        let tipoObjeto = contrato.tipo_objeto || 'Serviços';

        if (document.getElementById('resumoTitulo')) document.getElementById('resumoTitulo').innerText = `Contrato nº ${contrato.numero}`;
        if (document.getElementById('resumoEmpresa')) document.getElementById('resumoEmpresa').innerText = contrato.empresa;
        if (document.getElementById('resumoFiscal')) document.getElementById('resumoFiscal').innerText = contrato.fiscal || "Não designado";
        if (document.getElementById('resumoGmsVisualizador')) document.getElementById('resumoGmsVisualizador').innerText = contrato.gms || "-";
        if (document.getElementById('resumoCategoriaObjeto')) document.getElementById('resumoCategoriaObjeto').innerText = tipoObjeto;

        const valorTotal = parseFloat(contrato.valor_total || 0);
        if (document.getElementById('resumoValor')) {
            document.getElementById('resumoValor').innerText = valorTotal.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        }

        // Prazos e Vigência
        const diasRestantes = contrato.dias_restantes !== undefined ? contrato.dias_restantes : 0;
        const totalDiasContrato = contrato.total_dias || 365;
        const percentualTempoDecorrido = Math.min(100, Math.max(0, ((totalDiasContrato - diasRestantes) / totalDiasContrato) * 100));

        if (document.getElementById('resumoDias')) document.getElementById('resumoDias').innerText = contrato.data_fim_formatada || "-";
        
        const badgeDias = document.getElementById('resumoDiasBadge');
        if (badgeDias) {
            badgeDias.innerText = `${diasRestantes} dias restantes`;
            badgeDias.classList.remove('d-none');
        }

        const barraTempo = document.getElementById('barraProgressoTempo');
        if (barraTempo) {
            barraTempo.style.width = percentualTempoDecorrido + '%';
            barraTempo.className = "progress-bar";
            if (diasRestantes <= 30) {
                barraTempo.classList.add('bg-danger');
                if (badgeDias) badgeDias.className = "badge bg-danger text-white";
            } else if (diasRestantes <= 90) {
                barraTempo.classList.add('bg-warning', 'text-dark');
                if (badgeDias) badgeDias.className = "badge bg-warning text-dark";
            } else {
                barraTempo.classList.add('bg-success');
                if (badgeDias) badgeDias.className = "badge bg-success text-white";
            }
        }

        // Progresso Financeiro
        const valorPago = parseFloat(contrato.valor_pago || 0);
        const saldoRestante = valorTotal - valorPago;
        const percPago = valorTotal > 0 ? Math.round((valorPago / valorTotal) * 100) : 0;

        if (document.getElementById('barraProgressoFinanceiro')) document.getElementById('barraProgressoFinanceiro').style.width = percPago + '%';
        if (document.getElementById('resumoSaldoRestante')) document.getElementById('resumoSaldoRestante').innerText = `Saldo Restante: ${saldoRestante.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}`;
        if (document.getElementById('percExecFinanceira')) document.getElementById('percExecFinanceira').innerText = `${percPago}% Pago`;
        if (document.getElementById('barraExecFinanceira')) document.getElementById('barraExecFinanceira').style.width = percPago + '%';
        if (document.getElementById('execFinPaga')) document.getElementById('execFinPaga').innerText = valorPago.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        if (document.getElementById('execFinSaldo')) document.getElementById('execFinSaldo').innerText = saldoRestante.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

        // Tabela de Itens Unificada
        const tabelaItensUnificada = document.getElementById('tabela-itens-contrato');
        
        if (tabelaItensUnificada) {
            tabelaItensUnificada.innerHTML = '';

            if (contrato.itens && contrato.itens.length > 0) {
                let totalItensContratados = 0;
                let totalItensEntregues = 0;

                contrato.itens.forEach((item, index) => {
                    const qtdContratada = parseFloat(item.quantidade || 0);
                    const itemQtdEntregue = parseFloat(item.qtd_consumida || 0);
                    const valorUnitario = parseFloat(item.valor || 0);
                    const valorTotalItem = qtdContratada * valorUnitario;

                    totalItensContratados += qtdContratada;
                    totalItensEntregues += itemQtdEntregue;

                    const saldoDisponivel = Math.max(0, qtdContratada - itemQtdEntregue);
                    const percConsumoItem = qtdContratada > 0 ? Math.round((itemQtdEntregue / qtdContratada) * 100) : 0;

                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${String(index + 1).padStart(2, '0')}</td>
                        <td>
                            <span class="badge bg-secondary-subtle text-dark extra-small mb-1" style="font-size: 0.7rem;">${tipoObjeto}</span><br>
                            <strong>${item.categoria || 'Item'}</strong> - ${item.descricao || ''}
                        </td>
                        <td>${qtdContratada} un</td>
                        <td>${itemQtdEntregue} un</td>
                        <td class="fw-bold ${saldoDisponivel > 0 ? 'text-primary' : 'text-danger'}">${saldoDisponivel} un</td>
                        <td>${valorUnitario.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</td>
                        <td>${valorTotalItem.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</td>
                        <td>
                            <div class="progress" style="height: 6px; width: 100%;">
                                <div class="progress-bar bg-primary" style="width: ${percConsumoItem}%"></div>
                            </div>
                            <small class="text-muted extra-small">${percConsumoItem}%</small>
                        </td>
                    `;
                    tabelaItensUnificada.appendChild(tr);
                });

                // Atualização dos cards de desempenho físico geral
                const percFisicoGeral = totalItensContratados > 0 ? Math.round((totalItensEntregues / totalItensContratados) * 100) : 0;
                if (document.getElementById('percExecFisica')) document.getElementById('percExecFisica').innerText = `${percFisicoGeral}% Concluído`;
                if (document.getElementById('barraExecFisica')) document.getElementById('barraExecFisica').style.width = percFisicoGeral + '%';
                if (document.getElementById('execFisMedida')) document.getElementById('execFisMedida').innerText = `${totalItensEntregues} un`;
                if (document.getElementById('execFisRestante')) document.getElementById('execFisRestante').innerText = `${Math.max(0, totalItensContratados - totalItensEntregues)} un`;
            
            } else {
                tabelaItensUnificada.innerHTML = `
                    <tr>
                        <td colspan="8" class="text-center text-muted py-4">Nenhum item vinculado a este contrato.</td>
                    </tr>
                `;
            }
        }
    }
});
