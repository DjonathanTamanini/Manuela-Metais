let clientes = [];

// Carregar clientes
async function loadClientes() {
    try {
        const response = await fetch('/api/clientes');
        clientes = await response.json();
        renderTable();
    } catch (error) {
        console.error('Erro ao carregar clientes:', error);
    }
}

// Renderizar tabela
function renderTable() {
    const tbody = document.querySelector('#clientes-table tbody');
    tbody.innerHTML = '';

    if (clientes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 40px;">Nenhum cliente cadastrado</td></tr>';
        return;
    }

    clientes.forEach(cliente => {
        const saldo = parseFloat(cliente.saldo || 0);
        let saldoClass = 'saldo-zero';
        let saldoText = 'Quitado';
        
        if (saldo > 0) {
            saldoClass = 'saldo-positivo';
            saldoText = `Crédito: R$ ${saldo.toFixed(2).replace('.', ',')}`;
        } else if (saldo < 0) {
            saldoClass = 'saldo-negativo';
            saldoText = `Deve: R$ ${Math.abs(saldo).toFixed(2).replace('.', ',')}`;
        }

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${cliente.id}</td>
            <td><strong>${cliente.nome}</strong></td>
            <td>${cliente.cpf_cnpj}</td>
            <td>${cliente.telefone || '-'}</td>
            <td>${cliente.email || '-'}</td>
            <td><span class="badge ${saldoClass}">${saldoText}</span></td>
            <td>
                <button class="btn btn-danger btn-sm" onclick="deleteCliente(${cliente.id})">Excluir</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Abrir modal
function openModal() {
    document.getElementById('modal').classList.add('active');
}

// Fechar modal
function closeModal() {
    document.getElementById('modal').classList.remove('active');
    document.getElementById('cliente-form').reset();
}

// Salvar cliente
document.getElementById('cliente-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const cliente = {
        nome: formData.get('nome'),
        cpf_cnpj: formData.get('cpf_cnpj'),
        telefone: formData.get('telefone'),
        email: formData.get('email'),
        endereco: formData.get('endereco'),
        cidade: formData.get('cidade'),
        estado: formData.get('estado')
    };

    try {
        const response = await fetch('/api/clientes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(cliente)
        });

        if (response.ok) {
            closeModal();
            loadClientes();
        }
    } catch (error) {
        console.error('Erro ao salvar cliente:', error);
        alert('Erro ao salvar cliente');
    }
});

// Deletar cliente
async function deleteCliente(id) {
    if (!confirm('Tem certeza que deseja excluir este cliente?')) return;

    try {
        const response = await fetch(`/api/clientes/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadClientes();
        }
    } catch (error) {
        console.error('Erro ao deletar cliente:', error);
        alert('Erro ao deletar cliente');
    }
}

// Fechar modal ao clicar fora
document.getElementById('modal').addEventListener('click', (e) => {
    if (e.target.id === 'modal') closeModal();
});

// Carregar ao iniciar
loadClientes();
