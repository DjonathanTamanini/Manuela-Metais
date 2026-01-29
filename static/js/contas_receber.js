let contas = [];
let clientes = [];
let tipoAtual = '';

// Carregar dados
async function loadData() {
    try {
        const [contasRes, clientesRes] = await Promise.all([
            fetch('/api/contas-receber'),
            fetch('/api/clientes')
        ]);
        contas = await contasRes.json();
        clientes = await clientesRes.json();
        
        renderTable();
        renderSaldos();
        populateClienteSelect();
    } catch (error) {
        console.error('Erro ao carregar dados:', error);
    }
}

// Popular select de clientes
function populateClienteSelect() {
    const select = document.getElementById('cliente-select');
    select.innerHTML = '<option value="">Selecione um cliente</option>';
    
    clientes.forEach(cliente => {
        const option = document.createElement('option');
        option.value = cliente.id;
        option.textContent = cliente.nome;
        select.appendChild(option);
    });
}

// Mostrar saldo atual ao selecionar cliente
document.getElementById('cliente-select').addEventListener('change', function() {
    const clienteId = parseInt(this.value);
    const saldoDisplay = document.getElementById('saldo-atual-display');
    
    if (!clienteId) {
        saldoDisplay.innerHTML = '';
        return;
    }
    
    const cliente = clientes.find(c => c.id === clienteId);
    if (cliente) {
        const saldo = parseFloat(cliente.saldo || 0);
        let html = '<div style="padding: 15px; border-radius: 5px; margin-bottom: 10px; ';
        
        if (saldo > 0) {
            html += 'background: #d4edda; color: #155724;">🟢 Cliente com CRÉDITO de R$ ' + saldo.toFixed(2).replace('.', ',');
        } else if (saldo < 0) {
            html += 'background: #f8d7da; color: #721c24;">🔴 Cliente NEGATIVADO em R$ ' + Math.abs(saldo).toFixed(2).replace('.', ',');
        } else {
            html += 'background: #e2e3e5; color: #383d41;">⚪ Cliente QUITADO (saldo zero)';
        }
        
        html += '</div>';
        saldoDisplay.innerHTML = html;
    }
});

// Renderizar tabela
function renderTable() {
    const tbody = document.querySelector('#contas-table tbody');
    tbody.innerHTML = '';

    if (contas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 40px;">Nenhuma conta cadastrada</td></tr>';
        return;
    }

    contas.forEach(conta => {
        const cliente = clientes.find(c => c.id === parseInt(conta.cliente_id));
        const clienteNome = cliente ? cliente.nome : 'Cliente não encontrado';
        
        const statusClass = conta.status === 'pendente' ? 'badge-warning' : 
                           conta.status === 'recebido' ? 'badge-success' : 'badge-info';
        
        const tipoClass = conta.tipo === 'venda' ? 'badge-danger' : 'badge-success';
        const tipoText = conta.tipo === 'venda' ? '🔴 Venda (negativação)' : '🟢 Pagamento';

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${conta.id}</td>
            <td>${conta.data_vencimento || '-'}</td>
            <td><strong>${clienteNome}</strong></td>
            <td><span class="badge ${tipoClass}">${tipoText}</span></td>
            <td>${conta.descricao || '-'}</td>
            <td>R$ ${parseFloat(conta.valor).toFixed(2).replace('.', ',')}</td>
            <td><span class="badge ${statusClass}">${conta.status}</span></td>
            <td>
                ${conta.status === 'pendente' && conta.tipo === 'venda' ? 
                    `<button class="btn btn-success btn-sm" onclick="receberConta(${conta.id})">Receber</button>` : 
                    '-'}
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Renderizar saldos
function renderSaldos() {
    const container = document.getElementById('saldos-container');
    container.innerHTML = '';

    if (clientes.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #999;">Nenhum cliente cadastrado</p>';
        return;
    }

    const grid = document.createElement('div');
    grid.style.display = 'grid';
    grid.style.gridTemplateColumns = 'repeat(auto-fill, minmax(250px, 1fr))';
    grid.style.gap = '15px';

    clientes.forEach(cliente => {
        const saldo = parseFloat(cliente.saldo || 0);
        let cardClass = 'stat-card';
        let saldoText = '';
        let icon = '⚪';
        
        if (saldo > 0) {
            cardClass += ' positive';
            saldoText = 'Crédito: R$ ' + saldo.toFixed(2).replace('.', ',');
            icon = '🟢';
        } else if (saldo < 0) {
            cardClass += ' negative';
            saldoText = 'Deve: R$ ' + Math.abs(saldo).toFixed(2).replace('.', ',');
            icon = '🔴';
        } else {
            saldoText = 'Quitado';
        }

        const card = document.createElement('div');
        card.className = cardClass;
        card.innerHTML = `
            <h3>${icon} ${cliente.nome}</h3>
            <div class="value">${saldoText}</div>
        `;
        grid.appendChild(card);
    });

    container.appendChild(grid);
}

// Abrir modal
function openModal(tipo) {
    tipoAtual = tipo;
    document.getElementById('tipo-transacao').value = tipo;
    
    if (tipo === 'venda') {
        document.getElementById('modal-title').textContent = 'Registrar Venda (Cliente fica negativado)';
    } else {
        document.getElementById('modal-title').textContent = 'Receber Pagamento/Adiantamento';
    }
    
    document.getElementById('modal').classList.add('active');
}

// Fechar modal
function closeModal() {
    document.getElementById('modal').classList.remove('active');
    document.getElementById('conta-form').reset();
    document.getElementById('saldo-atual-display').innerHTML = '';
}

// Salvar conta
document.getElementById('conta-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const conta = {
        cliente_id: formData.get('cliente_id'),
        tipo: formData.get('tipo'),
        valor: formData.get('valor'),
        data_vencimento: formData.get('data_vencimento'),
        descricao: formData.get('descricao')
    };

    try {
        const response = await fetch('/api/contas-receber', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(conta)
        });

        if (response.ok) {
            closeModal();
            loadData();
            alert('Transação registrada com sucesso!');
        }
    } catch (error) {
        console.error('Erro ao salvar conta:', error);
        alert('Erro ao salvar conta');
    }
});

// Receber conta
async function receberConta(id) {
    if (!confirm('Confirmar recebimento desta conta?')) return;

    try {
        const response = await fetch(`/api/contas-receber/${id}/receber`, {
            method: 'POST'
        });

        if (response.ok) {
            loadData();
            alert('Conta recebida com sucesso!');
        }
    } catch (error) {
        console.error('Erro ao receber conta:', error);
        alert('Erro ao receber conta');
    }
}

// Fechar modal ao clicar fora
document.getElementById('modal').addEventListener('click', (e) => {
    if (e.target.id === 'modal') closeModal();
});

// Carregar ao iniciar
loadData();
