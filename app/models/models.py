from .. import db
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    cargo = db.Column(db.String(20), default='FUNCIONARIO')  # ADMIN, DONO, GERENTE, FUNCIONARIO

class Produto(db.Model):
    __tablename__ = 'produtos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco_quilo = db.Column(db.Float, nullable=False)
    estoque_atual = db.Column(db.Float, default=0.0)

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    documento = db.Column(db.String(20))
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(255))
    saldo = db.Column(db.Float, default=0.0)  # Negativo = deve para empresa

class Fornecedor(db.Model):
    __tablename__ = 'fornecedores'
    id = db.Column(db.Integer, primary_key=True)
    nome_fantasia = db.Column(db.String(100), nullable=False)
    razao_social = db.Column(db.String(150))
    cnpj = db.Column(db.String(18))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    endereco = db.Column(db.String(255))
    saldo = db.Column(db.Float, default=0.0)  # Negativo = você deve para fornecedor
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    id_produto = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    id_fornecedor = db.Column(db.Integer, db.ForeignKey('fornecedores.id'))
    peso = db.Column(db.Float, nullable=False)  # Positivo = compra, Negativo = venda
    valor_total = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(10), default='VENDA')  # VENDA ou COMPRA
    data_pedido = db.Column(db.DateTime, default=datetime.utcnow)

class Financeiro(db.Model):
    __tablename__ = 'financeiro'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(255))
    valor = db.Column(db.Float)
    tipo = db.Column(db.String(10))  # Entrada ou Saída
    categoria = db.Column(db.String(50))  # Ex: Venda, Compra, Aluguel, Salário
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)

class ContaPagar(db.Model):
    __tablename__ = 'contas_pagar'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data_vencimento = db.Column(db.Date, nullable=False)
    data_pagamento = db.Column(db.Date)  # NULL = não pago
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedores.id'))
    categoria = db.Column(db.String(50))  # Aluguel, Salário, Fornecedor, etc
    status = db.Column(db.String(20), default='PENDENTE')  # PENDENTE, PAGO, ATRASADO
    observacoes = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento
    fornecedor = db.relationship('Fornecedor', backref='contas')