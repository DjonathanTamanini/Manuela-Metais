from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'manuela-metais-2026'

# Simulação de banco de dados em arquivo JSON
DATA_FILE = 'data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'funcionarios': [],
        'fornecedores': [],
        'clientes': [],
        'produtos': [],
        'estoque': [],
        'contas_pagar': [],
        'contas_receber': [],
        'gastos': [],
        'pedidos_compra': []
    }

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

# FUNCIONÁRIOS
@app.route('/funcionarios')
def funcionarios():
    data = load_data()
    return render_template('funcionarios.html', funcionarios=data['funcionarios'])

@app.route('/api/funcionarios', methods=['GET', 'POST'])
def api_funcionarios():
    data = load_data()
    
    if request.method == 'POST':
        funcionario = request.json
        funcionario['id'] = len(data['funcionarios']) + 1
        funcionario['data_cadastro'] = datetime.now().strftime('%Y-%m-%d')
        data['funcionarios'].append(funcionario)
        save_data(data)
        return jsonify(funcionario), 201
    
    return jsonify(data['funcionarios'])

@app.route('/api/funcionarios/<int:id>', methods=['DELETE'])
def delete_funcionario(id):
    data = load_data()
    data['funcionarios'] = [f for f in data['funcionarios'] if f['id'] != id]
    save_data(data)
    return '', 204

# FORNECEDORES
@app.route('/fornecedores')
def fornecedores():
    data = load_data()
    return render_template('fornecedores.html', fornecedores=data['fornecedores'])

@app.route('/api/fornecedores', methods=['GET', 'POST'])
def api_fornecedores():
    data = load_data()
    
    if request.method == 'POST':
        fornecedor = request.json
        fornecedor['id'] = len(data['fornecedores']) + 1
        data['fornecedores'].append(fornecedor)
        save_data(data)
        return jsonify(fornecedor), 201
    
    return jsonify(data['fornecedores'])

@app.route('/api/fornecedores/<int:id>', methods=['DELETE'])
def delete_fornecedor(id):
    data = load_data()
    data['fornecedores'] = [f for f in data['fornecedores'] if f['id'] != id]
    save_data(data)
    return '', 204

# CLIENTES
@app.route('/clientes')
def clientes():
    data = load_data()
    return render_template('clientes.html', clientes=data['clientes'])

@app.route('/api/clientes', methods=['GET', 'POST'])
def api_clientes():
    data = load_data()
    
    if request.method == 'POST':
        cliente = request.json
        cliente['id'] = len(data['clientes']) + 1
        cliente['saldo'] = 0.0  # Saldo inicial
        data['clientes'].append(cliente)
        save_data(data)
        return jsonify(cliente), 201
    
    return jsonify(data['clientes'])

@app.route('/api/clientes/<int:id>', methods=['DELETE', 'PUT'])
def manage_cliente(id):
    data = load_data()
    
    if request.method == 'DELETE':
        data['clientes'] = [c for c in data['clientes'] if c['id'] != id]
        save_data(data)
        return '', 204
    
    if request.method == 'PUT':
        cliente_data = request.json
        for cliente in data['clientes']:
            if cliente['id'] == id:
                cliente.update(cliente_data)
                save_data(data)
                return jsonify(cliente)
        return jsonify({'error': 'Cliente não encontrado'}), 404

# PRODUTOS
@app.route('/produtos')
def produtos():
    data = load_data()
    return render_template('produtos.html', produtos=data['produtos'])

@app.route('/api/produtos', methods=['GET', 'POST'])
def api_produtos():
    data = load_data()
    
    if request.method == 'POST':
        produto = request.json
        produto['id'] = len(data['produtos']) + 1
        data['produtos'].append(produto)
        save_data(data)
        return jsonify(produto), 201
    
    return jsonify(data['produtos'])

@app.route('/api/produtos/<int:id>', methods=['DELETE'])
def delete_produto(id):
    data = load_data()
    data['produtos'] = [p for p in data['produtos'] if p['id'] != id]
    save_data(data)
    return '', 204

# ESTOQUE
@app.route('/estoque')
def estoque():
    data = load_data()
    return render_template('estoque.html', estoque=data['estoque'], produtos=data['produtos'])

@app.route('/api/estoque', methods=['GET', 'POST'])
def api_estoque():
    data = load_data()
    
    if request.method == 'POST':
        movimento = request.json
        movimento['id'] = len(data['estoque']) + 1
        movimento['data'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        data['estoque'].append(movimento)
        save_data(data)
        return jsonify(movimento), 201
    
    return jsonify(data['estoque'])

# CONTAS A PAGAR
@app.route('/contas-pagar')
def contas_pagar():
    data = load_data()
    return render_template('contas_pagar.html', contas=data['contas_pagar'], fornecedores=data['fornecedores'])

@app.route('/api/contas-pagar', methods=['GET', 'POST'])
def api_contas_pagar():
    data = load_data()
    
    if request.method == 'POST':
        conta = request.json
        conta['id'] = len(data['contas_pagar']) + 1
        conta['status'] = 'pendente'
        data['contas_pagar'].append(conta)
        save_data(data)
        return jsonify(conta), 201
    
    return jsonify(data['contas_pagar'])

@app.route('/api/contas-pagar/<int:id>/pagar', methods=['POST'])
def pagar_conta(id):
    data = load_data()
    for conta in data['contas_pagar']:
        if conta['id'] == id:
            conta['status'] = 'pago'
            conta['data_pagamento'] = datetime.now().strftime('%Y-%m-%d')
            save_data(data)
            return jsonify(conta)
    return jsonify({'error': 'Conta não encontrada'}), 404

# CONTAS A RECEBER
@app.route('/contas-receber')
def contas_receber():
    data = load_data()
    return render_template('contas_receber.html', contas=data['contas_receber'], clientes=data['clientes'])

@app.route('/api/contas-receber', methods=['GET', 'POST'])
def api_contas_receber():
    data = load_data()
    
    if request.method == 'POST':
        conta = request.json
        conta['id'] = len(data['contas_receber']) + 1
        conta['status'] = 'pendente'
        
        # Atualiza saldo do cliente
        cliente_id = int(conta['cliente_id'])
        for cliente in data['clientes']:
            if cliente['id'] == cliente_id:
                # Se for venda, diminui saldo (fica negativo)
                # Se for pagamento/adiantamento, aumenta saldo
                if conta.get('tipo') == 'venda':
                    cliente['saldo'] = cliente.get('saldo', 0) - float(conta['valor'])
                elif conta.get('tipo') == 'pagamento':
                    cliente['saldo'] = cliente.get('saldo', 0) + float(conta['valor'])
                break
        
        data['contas_receber'].append(conta)
        save_data(data)
        return jsonify(conta), 201
    
    return jsonify(data['contas_receber'])

@app.route('/api/contas-receber/<int:id>/receber', methods=['POST'])
def receber_conta(id):
    data = load_data()
    for conta in data['contas_receber']:
        if conta['id'] == id:
            conta['status'] = 'recebido'
            conta['data_recebimento'] = datetime.now().strftime('%Y-%m-%d')
            
            # Atualiza saldo do cliente
            cliente_id = int(conta['cliente_id'])
            for cliente in data['clientes']:
                if cliente['id'] == cliente_id:
                    cliente['saldo'] = cliente.get('saldo', 0) + float(conta['valor'])
                    break
            
            save_data(data)
            return jsonify(conta)
    return jsonify({'error': 'Conta não encontrada'}), 404

# GASTOS
@app.route('/gastos')
def gastos():
    data = load_data()
    return render_template('gastos.html', gastos=data['gastos'])

@app.route('/api/gastos', methods=['GET', 'POST'])
def api_gastos():
    data = load_data()
    
    if request.method == 'POST':
        gasto = request.json
        gasto['id'] = len(data['gastos']) + 1
        gasto['data'] = datetime.now().strftime('%Y-%m-%d')
        data['gastos'].append(gasto)
        save_data(data)
        return jsonify(gasto), 201
    
    return jsonify(data['gastos'])

# PEDIDOS DE COMPRA
@app.route('/pedidos-compra')
def pedidos_compra():
    data = load_data()
    return render_template('pedidos_compra.html', pedidos=data['pedidos_compra'], fornecedores=data['fornecedores'], produtos=data['produtos'])

@app.route('/api/pedidos-compra', methods=['GET', 'POST'])
def api_pedidos_compra():
    data = load_data()
    
    if request.method == 'POST':
        pedido = request.json
        pedido['id'] = len(data['pedidos_compra']) + 1
        pedido['data'] = datetime.now().strftime('%Y-%m-%d')
        pedido['status'] = 'pendente'
        data['pedidos_compra'].append(pedido)
        save_data(data)
        return jsonify(pedido), 201
    
    return jsonify(data['pedidos_compra'])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
