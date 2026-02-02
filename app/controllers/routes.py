from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    current_app as app
)
from .. import db, bcrypt
from app.models.models import Produto, Cliente, Pedido, Usuario, Fornecedor, ContaPagar, Financeiro

import functools
import traceback
import os
from datetime import datetime, timedelta

login_attempts = {}

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash("Você precisa estar logado.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def roles_accepted(*roles):
    def wrapper(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('usuario_cargo') not in roles:
                flash(
                    "Seu cargo não tem permissão para acessar esta página.",
                    "danger"
                )
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ip = request.remote_addr
        now = datetime.utcnow()

        if ip in login_attempts:
            login_attempts[ip] = [
                t for t in login_attempts[ip]
                if now - t < timedelta(minutes=1)
            ]
        else:
            login_attempts[ip] = []

        if len(login_attempts[ip]) >= 5:
            flash(
                "Muitas tentativas de login. Aguarde 1 minuto e tente novamente.",
                "danger"
            )
            app.logger.warning(f"Rate limit excedido para IP: {ip}")
            return render_template('login.html')

        login_attempts[ip].append(now)

        try:
            email = request.form.get('login_usuario', '').strip().lower()
            senha = request.form.get('senha', '')

            if not email or not senha:
                flash("Preencha todos os campos!", "danger")
                return render_template('login.html')

            user = Usuario.query.filter_by(email=email).first()

            if user and bcrypt.check_password_hash(user.senha, senha):
                session.permanent = True
                session.update({
                    'usuario_id': user.id,
                    'usuario_nome': user.nome,
                    'usuario_cargo': user.cargo
                })

                if ip in login_attempts:
                    login_attempts[ip] = []

                app.logger.info(f"Login bem-sucedido: {user.email}")
                return redirect(url_for('dashboard'))

            app.logger.warning(f"Tentativa de login falhou para: {email}")
            flash("Login ou senha incorretos!", "danger")

        except Exception as e:
            app.logger.error(
                f"Erro no login: {e}\n{traceback.format_exc()}"
            )
            flash("Erro ao processar login.", "warning")

    return render_template('login.html')


@app.route('/logout')
def logout():
    usuario = session.get('usuario_nome', 'Anônimo')
    session.clear()
    app.logger.info(f"Logout: {usuario}")
    flash("Você saiu com sucesso.", "info")
    return redirect(url_for('login'))


@app.route('/')
@login_required
def dashboard():
    try:
        estoque = (
            db.session.query(db.func.sum(Produto.estoque_atual)).scalar() or 0
        )

        a_receber = (
            db.session.query(db.func.sum(Cliente.saldo))
            .filter(Cliente.saldo < 0)
            .scalar()
            or 0
        )

        produtos_db = Produto.query.all()
        nomes_produtos = [p.nome for p in produtos_db]
        valores_produtos = [float(p.estoque_atual) for p in produtos_db]

        alertas = Produto.query.filter(
            Produto.estoque_atual < 50
        ).all()

        return render_template(
            'dashboard.html',
            estoque=estoque,
            a_receber=abs(a_receber),
            nomes_produtos=nomes_produtos,
            valores_produtos=valores_produtos,
            alertas=alertas
        )

    except Exception as e:
        app.logger.error(
            f"Erro no dashboard: {e}\n{traceback.format_exc()}"
        )
        return "Erro ao carregar painel", 500


@app.route('/usuarios', methods=['GET', 'POST'])
@login_required
@roles_accepted('ADMIN', 'DONO', 'GERENTE')
def gerenciar_usuarios():
    if request.method == 'POST':
        try:
            nome = request.form.get('nome')
            email = request.form.get('email', '').lower().strip()
            senha = request.form.get('senha')
            cargo_alvo = request.form.get('cargo')
            meu_cargo = session.get('usuario_cargo')

            # Regra de Hierarquia para criação
            pode_criar = False
            if meu_cargo == 'ADMIN': pode_criar = True
            elif meu_cargo == 'DONO' and cargo_alvo != 'ADMIN': pode_criar = True
            elif meu_cargo == 'GERENTE' and cargo_alvo == 'FUNCIONARIO': pode_criar = True

            if pode_criar:
                hash_s = bcrypt.generate_password_hash(senha).decode('utf-8')
                novo = Usuario(nome=nome, email=email, senha=hash_s, cargo=cargo_alvo)
                db.session.add(novo)
                db.session.commit()
                flash(f"Usuário {nome} cadastrado com sucesso!", "success")
            else:
                flash("Você não tem permissão para criar um usuário com este cargo.", "danger")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erro ao criar usuário: {e}")
            flash("Erro ao cadastrar. Verifique se o e-mail já existe.", "danger")

    usuarios = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/estoque')
@login_required
def estoque():
    try:
        produtos = Produto.query.all()
        clientes = Cliente.query.all()
        return render_template(
            'estoque.html',
            produtos=produtos,
            clientes=clientes
        )
    except Exception as e:
        app.logger.error(
            f"Erro ao carregar estoque: {e}\n{traceback.format_exc()}"
        )
        flash("Erro ao carregar estoque.", "danger")
        return redirect(url_for('dashboard'))

@app.route('/editar_usuario/<int:id>', methods=['POST'])
@login_required
@roles_accepted('ADMIN', 'DONO')
def editar_usuario(id):
    try:
        user = Usuario.query.get_or_404(id)
        user.nome = request.form.get('nome')
        user.email = request.form.get('email', '').lower().strip()
        user.cargo = request.form.get('cargo')
        
        # Só altera a senha se o campo não estiver vazio
        nova_senha = request.form.get('senha')
        if nova_senha:
            user.senha = bcrypt.generate_password_hash(nova_senha).decode('utf-8')
            
        db.session.commit()
        flash(f"Dados de {user.nome} atualizados!", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erro ao editar usuário {id}: {e}")
        flash("Erro ao atualizar dados.", "danger")
    return redirect(url_for('gerenciar_usuarios'))

@app.route('/editar_produto/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_produto(id):
    produto = Produto.query.get_or_404(id)

    if request.method == 'POST':
        try:
            nome = request.form.get('nome', '').strip()
            preco = float(request.form.get('preco', 0))
            estoque_val = float(request.form.get('estoque_atual', 0))

            if not nome or preco <= 0 or estoque_val < 0:
                flash("Dados inválidos!", "danger")
                return render_template(
                    'editar_produto.html',
                    produto=produto
                )

            produto.nome = nome
            produto.preco_quilo = preco
            produto.estoque_atual = estoque_val
            db.session.commit()

            app.logger.info(
                f"Produto editado: {produto.nome} (ID: {id})"
            )
            flash("Produto atualizado com sucesso!", "success")
            return redirect(url_for('estoque'))

        except ValueError:
            flash("Valores numéricos inválidos!", "danger")

        except Exception as e:
            db.session.rollback()
            app.logger.error(
                f"Erro ao editar produto: {e}\n{traceback.format_exc()}"
            )
            flash("Erro ao salvar alterações.", "danger")

    return render_template('editar_produto.html', produto=produto)

@app.route('/registrar_venda', methods=['POST'])
@login_required
def registrar_venda():
    try:
        prod_id = int(request.form.get('id_produto'))
        cli_id = int(request.form.get('id_cliente'))
        peso = float(request.form.get('peso'))
        valor_total = float(request.form.get('valor_total'))
        pago = request.form.get('pago')

        produto = Produto.query.get(prod_id)
        cliente = Cliente.query.get(cli_id)

        # Verificação de Estoque
        if produto.estoque_atual < peso:
            flash(f"Estoque insuficiente! Você tem apenas {produto.estoque_atual}kg de {produto.nome}.", "danger")
            return redirect(url_for('pagina_vendas'))

        # Lógica: Sai do estoque
        produto.estoque_atual -= peso
        
        # Lógica: Se não pagou, o saldo do cliente aumenta (ele deve para a empresa)
        # Se você usa saldo negativo para dívidas, aqui seria: cliente.saldo += valor_total
        if pago == 'nao':
            cliente.saldo -= valor_total # Seguindo sua lógica de saldo negativo = dívida

        novo_pedido = Pedido(id_produto=prod_id, id_cliente=cli_id, peso=-peso, valor_total=valor_total)
        db.session.add(novo_pedido)
        db.session.commit()
        
        flash(f"Venda de {peso}kg de {produto.nome} realizada!", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erro na venda: {e}")
        flash("Erro ao processar venda.", "danger")
    
    return redirect(url_for('pagina_vendas'))

@app.route('/vendas')
@login_required
def pagina_vendas():
    produtos = Produto.query.all()
    clientes = Cliente.query.all()
    # Pega as últimas 10 vendas (pedidos com peso negativo)
    ultimas_vendas = Pedido.query.filter(Pedido.peso < 0).order_by(Pedido.id.desc()).limit(10).all()
    return render_template('vendas.html', produtos=produtos, clientes=clientes, vendas=ultimas_vendas)

@app.route('/clientes')
@login_required
def lista_clientes():
    try:
        clientes = Cliente.query.all()
        return render_template(
            'clientes.html',
            clientes=clientes
        )
    except Exception as e:
        app.logger.error(
            f"Erro ao listar clientes: {e}\n{traceback.format_exc()}"
        )
        flash("Erro ao carregar clientes.", "danger")
        return redirect(url_for('dashboard'))


@app.route('/editar_cliente/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)

    if request.method == 'POST':
        try:
            nome = request.form.get('nome', '').strip()
            if not nome:
                flash("Nome do cliente é obrigatório!", "danger")
                return render_template(
                    'editar_cliente.html',
                    cliente=cliente
                )

            cliente.nome = nome
            cliente.documento = request.form.get('documento', '').strip()

            if hasattr(cliente, 'telefone'):
                cliente.telefone = request.form.get('telefone', '')

            if hasattr(cliente, 'endereco'):
                cliente.endereco = request.form.get('endereco', '')

            db.session.commit()
            app.logger.info(
                f"Cliente editado: {cliente.nome} (ID: {id})"
            )
            flash("Cliente atualizado com sucesso!", "success")
            return redirect(url_for('lista_clientes'))

        except Exception as e:
            db.session.rollback()
            app.logger.error(
                f"Erro ao editar cliente: {e}\n{traceback.format_exc()}"
            )
            flash("Erro ao salvar alterações.", "danger")

    return render_template('editar_cliente.html', cliente=cliente)


@app.route('/historico_cliente/<int:id>')
@login_required
def historico_cliente(id):
    try:
        cliente = Cliente.query.get_or_404(id)
        compras = (
            db.session.query(
                Pedido,
                Produto.nome.label('nome_produto')
            )
            .join(Produto, Pedido.id_produto == Produto.id)
            .filter(Pedido.id_cliente == id)
            .order_by(Pedido.data_pedido.desc())
            .all()
        )
        return render_template(
            'historico.html',
            cliente=cliente,
            compras=compras
        )
    except Exception as e:
        app.logger.error(
            f"Erro ao carregar histórico: {e}\n{traceback.format_exc()}"
        )
        flash("Erro ao carregar histórico.", "danger")
        return redirect(url_for('lista_clientes'))

@app.route('/fornecedores')
@login_required
def lista_fornecedores():
    """Lista todos os fornecedores cadastrados"""
    try:
        fornecedores = Fornecedor.query.all()
        return render_template('fornecedores.html', fornecedores=fornecedores)
    except Exception as e:
        app.logger.error(f"Erro ao listar fornecedores: {e}\n{traceback.format_exc()}")
        flash("Erro ao carregar fornecedores.", "danger")
        return redirect(url_for('dashboard'))

@app.route('/cadastrar_fornecedor', methods=['POST'])
@login_required
@roles_accepted('ADMIN', 'DONO', 'GERENTE')
def cadastrar_fornecedor():
    """Cadastra novo fornecedor"""
    try:
        nome_fantasia = request.form.get('nome_fantasia', '').strip()
        
        if not nome_fantasia:
            flash("Nome fantasia é obrigatório!", "danger")
            return redirect(url_for('lista_fornecedores'))
        
        novo = Fornecedor(
            nome_fantasia=nome_fantasia,
            razao_social=request.form.get('razao_social', '').strip(),
            cnpj=request.form.get('cnpj', '').strip(),
            telefone=request.form.get('telefone', '').strip(),
            email=request.form.get('email', '').strip(),
            endereco=request.form.get('endereco', '').strip(),
            saldo=0.0
        )
        
        db.session.add(novo)
        db.session.commit()
        
        app.logger.info(f"Fornecedor cadastrado: {nome_fantasia}")
        flash(f"Fornecedor {nome_fantasia} cadastrado com sucesso!", "success")
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erro ao cadastrar fornecedor: {e}\n{traceback.format_exc()}")
        flash("Erro ao cadastrar. Verifique se o CNPJ já existe.", "danger")
    
    return redirect(url_for('lista_fornecedores'))

@app.route('/editar_fornecedor/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('ADMIN', 'DONO', 'GERENTE')
def editar_fornecedor(id):
    """Edita dados de um fornecedor"""
    fornecedor = Fornecedor.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            nome_fantasia = request.form.get('nome_fantasia', '').strip()
            
            if not nome_fantasia:
                flash("Nome fantasia é obrigatório!", "danger")
                return render_template('editar_fornecedor.html', fornecedor=fornecedor)
            
            fornecedor.nome_fantasia = nome_fantasia
            fornecedor.razao_social = request.form.get('razao_social', '').strip()
            fornecedor.cnpj = request.form.get('cnpj', '').strip()
            fornecedor.telefone = request.form.get('telefone', '').strip()
            fornecedor.email = request.form.get('email', '').strip()
            fornecedor.endereco = request.form.get('endereco', '').strip()
            
            db.session.commit()
            
            app.logger.info(f"Fornecedor editado: {fornecedor.nome_fantasia} (ID: {id})")
            flash("Fornecedor atualizado com sucesso!", "success")
            return redirect(url_for('lista_fornecedores'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Erro ao editar fornecedor: {e}\n{traceback.format_exc()}")
            flash("Erro ao salvar alterações.", "danger")
    
    return render_template('editar_fornecedor.html', fornecedor=fornecedor)

@app.route('/deletar_fornecedor/<int:id>', methods=['POST'])
@login_required
@roles_accepted('ADMIN', 'DONO')
def deletar_fornecedor(id):
    """Deleta um fornecedor"""
    try:
        fornecedor = Fornecedor.query.get_or_404(id)
        nome = fornecedor.nome_fantasia
        
        # Verificar se tem contas pendentes
        contas_pendentes = ContaPagar.query.filter_by(
            fornecedor_id=id, 
            status='PENDENTE'
        ).count()
        
        if contas_pendentes > 0:
            flash(f"Não é possível deletar! {nome} possui {contas_pendentes} conta(s) pendente(s).", "danger")
            return redirect(url_for('lista_fornecedores'))
        
        db.session.delete(fornecedor)
        db.session.commit()
        
        app.logger.info(f"Fornecedor deletado: {nome} (ID: {id})")
        flash(f"Fornecedor {nome} deletado com sucesso!", "success")
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erro ao deletar fornecedor: {e}\n{traceback.format_exc()}")
        flash("Erro ao deletar fornecedor.", "danger")
    
    return redirect(url_for('lista_fornecedores'))


# ===== CONTAS A PAGAR =====

@app.route('/contas_pagar')
@login_required
@roles_accepted('ADMIN', 'DONO', 'GERENTE')
def contas_pagar():
    """Exibe todas as contas a pagar (pendentes e pagas)"""
    try:
        from datetime import date
        
        hoje = date.today()
        
        # Contas pendentes
        pendentes = ContaPagar.query.filter_by(status='PENDENTE').order_by(
            ContaPagar.data_vencimento
        ).all()
        
        # Atualizar status de atrasadas
        for conta in pendentes:
            if conta.data_vencimento < hoje and conta.status == 'PENDENTE':
                conta.status = 'ATRASADO'
        db.session.commit()
        
        # Separar por status
        atrasadas = [c for c in pendentes if c.status == 'ATRASADO']
        pendentes_em_dia = [c for c in pendentes if c.status == 'PENDENTE']
        
        # Contas pagas (últimas 20)
        pagas = ContaPagar.query.filter_by(status='PAGO').order_by(
            ContaPagar.data_pagamento.desc()
        ).limit(20).all()
        
        # Fornecedores para cadastro de nova conta
        fornecedores = Fornecedor.query.all()
        
        # Total a pagar
        total_pendente = sum(c.valor for c in pendentes if c.status in ['PENDENTE', 'ATRASADO'])
        
        return render_template(
            'contas_pagar.html',
            atrasadas=atrasadas,
            pendentes=pendentes_em_dia,
            pagas=pagas,
            fornecedores=fornecedores,
            total_pendente=total_pendente
        )
        
    except Exception as e:
        app.logger.error(f"Erro em contas a pagar: {e}\n{traceback.format_exc()}")
        flash("Erro ao carregar contas a pagar.", "danger")
        return redirect(url_for('dashboard'))

@app.route('/cadastrar_conta_pagar', methods=['POST'])
@login_required
@roles_accepted('ADMIN', 'DONO', 'GERENTE')
def cadastrar_conta_pagar():
    """Cadastra nova conta a pagar"""
    try:
        from datetime import datetime
        
        descricao = request.form.get('descricao', '').strip()
        valor = float(request.form.get('valor', 0))
        data_vencimento_str = request.form.get('data_vencimento')
        categoria = request.form.get('categoria', 'Outros')
        fornecedor_id = request.form.get('fornecedor_id')
        observacoes = request.form.get('observacoes', '').strip()
        
        if not descricao or valor <= 0:
            flash("Descrição e valor são obrigatórios!", "danger")
            return redirect(url_for('contas_pagar'))
        
        # Converter data
        data_vencimento = datetime.strptime(data_vencimento_str, '%Y-%m-%d').date()
        
        nova_conta = ContaPagar(
            descricao=descricao,
            valor=valor,
            data_vencimento=data_vencimento,
            categoria=categoria,
            fornecedor_id=int(fornecedor_id) if fornecedor_id else None,
            observacoes=observacoes,
            status='PENDENTE'
        )
        
        db.session.add(nova_conta)
        db.session.commit()
        
        app.logger.info(f"Conta a pagar cadastrada: {descricao} - R$ {valor}")
        flash(f"Conta '{descricao}' cadastrada com sucesso!", "success")
        
    except ValueError:
        flash("Erro: Verifique o valor e a data.", "danger")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erro ao cadastrar conta: {e}\n{traceback.format_exc()}")
        flash("Erro ao cadastrar conta a pagar.", "danger")
    
    return redirect(url_for('contas_pagar'))

@app.route('/pagar_conta/<int:id>', methods=['POST'])
@login_required
@roles_accepted('ADMIN', 'DONO', 'GERENTE')
def pagar_conta(id):
    """Marca uma conta como paga"""
    try:
        from datetime import date
        
        conta = ContaPagar.query.get_or_404(id)
        
        if conta.status == 'PAGO':
            flash("Esta conta já foi paga!", "warning")
            return redirect(url_for('contas_pagar'))
        
        # Marcar como paga
        conta.status = 'PAGO'
        conta.data_pagamento = date.today()
        
        # Registrar no financeiro
        registro_financeiro = Financeiro(
            descricao=f"Pagamento: {conta.descricao}",
            valor=conta.valor,
            tipo='Saída',
            categoria=conta.categoria
        )
        db.session.add(registro_financeiro)
        
        # Atualizar saldo do fornecedor se tiver
        if conta.fornecedor_id:
            fornecedor = Fornecedor.query.get(conta.fornecedor_id)
            if fornecedor:
                fornecedor.saldo += conta.valor  # Zera a dívida
        
        db.session.commit()
        
        app.logger.info(f"Conta paga: {conta.descricao} - R$ {conta.valor}")
        flash(f"Conta '{conta.descricao}' marcada como paga!", "success")
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erro ao pagar conta: {e}\n{traceback.format_exc()}")
        flash("Erro ao processar pagamento.", "danger")
    
    return redirect(url_for('contas_pagar'))

@app.route('/deletar_conta/<int:id>', methods=['POST'])
@login_required
@roles_accepted('ADMIN', 'DONO')
def deletar_conta(id):
    """Deleta uma conta a pagar"""
    try:
        conta = ContaPagar.query.get_or_404(id)
        descricao = conta.descricao
        
        db.session.delete(conta)
        db.session.commit()
        
        app.logger.info(f"Conta deletada: {descricao} (ID: {id})")
        flash(f"Conta '{descricao}' deletada com sucesso!", "success")
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erro ao deletar conta: {e}\n{traceback.format_exc()}")
        flash("Erro ao deletar conta.", "danger")
    
    return redirect(url_for('contas_pagar'))


# ===== PEDIDO DE COMPRA ATUALIZADO (usa fornecedor agora) =====

@app.route('/pedido_compra_fornecedor', methods=['POST'])
@login_required
def pedido_compra_fornecedor():
    """
    Registra compra de fornecedor (aumenta estoque)
    Diferente de pedido_compra que usava cliente
    """
    try:
        prod_id = int(request.form.get('id_produto'))
        forn_id = int(request.form.get('id_fornecedor'))
        peso = float(request.form.get('peso'))
        valor_total = float(request.form.get('valor_total'))
        pago = request.form.get('pago')

        if peso <= 0 or valor_total <= 0:
            flash("Peso e valor devem ser positivos!", "danger")
            return redirect(url_for('estoque'))

        produto = Produto.query.get(prod_id)
        fornecedor = Fornecedor.query.get(forn_id)

        if not produto or not fornecedor:
            flash("Produto ou Fornecedor não encontrado.", "danger")
            return redirect(url_for('estoque'))

        # Aumenta estoque
        produto.estoque_atual += peso

        # Se não pagou, você deve para o fornecedor
        if pago == 'nao':
            fornecedor.saldo -= valor_total  # Negativo = você deve

        # Registrar pedido
        novo_pedido = Pedido(
            id_produto=prod_id,
            id_fornecedor=forn_id,
            peso=peso,
            valor_total=valor_total,
            tipo='COMPRA'
        )
        db.session.add(novo_pedido)

        # Registrar no financeiro se foi pago
        if pago == 'sim':
            registro = Financeiro(
                descricao=f"Compra: {peso}kg de {produto.nome} - {fornecedor.nome_fantasia}",
                valor=valor_total,
                tipo='Saída',
                categoria='Compra'
            )
            db.session.add(registro)

        db.session.commit()

        app.logger.info(f"Compra registrada: {peso}kg de {produto.nome} - Fornecedor: {fornecedor.nome_fantasia}")
        flash("Compra registrada com sucesso!", "success")

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erro na compra: {e}\n{traceback.format_exc()}")
        flash("Erro ao processar compra.", "danger")

    return redirect(url_for('estoque'))

@app.route('/cadastrar/<tipo>', methods=['POST'])
@login_required
def cadastrar(tipo):
    try:
        if tipo == 'cliente':
            nome = request.form.get('nome', '').strip()
            if not nome:
                flash("Nome é obrigatório!", "danger")
                return redirect(
                    request.referrer or url_for('dashboard')
                )

            novo = Cliente(
                nome=nome,
                documento=request.form.get('documento', '').strip(),
                saldo=0.0
            )

        elif tipo == 'produto':
            nome = request.form.get('nome', '').strip()
            preco = float(request.form.get('preco', 0))
            estoque_inicial = float(
                request.form.get('estoque_atual', 0)
            )

            if not nome or preco <= 0 or estoque_inicial < 0:
                flash(
                    "Dados inválidos! Nome obrigatório, preço > 0, estoque >= 0.",
                    "danger"
                )
                return redirect(
                    request.referrer or url_for('dashboard')
                )

            novo = Produto(
                nome=nome,
                preco_quilo=preco,
                estoque_atual=estoque_inicial
            )
        else:
            flash("Tipo de cadastro inválido!", "danger")
            return redirect(url_for('dashboard'))

        db.session.add(novo)
        db.session.commit()
        app.logger.info(f"{tipo.capitalize()} cadastrado: {nome}")
        flash(
            f"{tipo.capitalize()} cadastrado com sucesso!",
            "success"
        )

    except ValueError:
        flash(
            "Erro: Verifique se os campos numéricos estão corretos.",
            "danger"
        )

    except Exception as e:
        db.session.rollback()
        app.logger.error(
            f"Erro no cadastro {tipo}: {e}\n{traceback.format_exc()}"
        )
        flash("Erro ao cadastrar.", "danger")

    return redirect(request.referrer or url_for('dashboard'))


@app.route('/pedido_compra', methods=['POST'])
@login_required
def pedido_compra():
    try:
        prod_id = int(request.form.get('id_produto'))
        cli_id = int(request.form.get('id_cliente'))
        peso = float(request.form.get('peso'))
        valor_total = float(request.form.get('valor_total'))
        pago = request.form.get('pago')

        if peso <= 0:
            flash("Peso deve ser maior que zero!", "danger")
            return redirect(url_for('estoque'))

        if valor_total <= 0:
            flash("Valor total deve ser maior que zero!", "danger")
            return redirect(url_for('estoque'))

        produto = Produto.query.get(prod_id)
        cliente = Cliente.query.get(cli_id)

        if not produto or not cliente:
            flash("Produto ou Cliente não encontrado.", "danger")
            return redirect(url_for('estoque'))

        produto.estoque_atual += peso

        if pago == 'nao':
            cliente.saldo -= valor_total

        novo_pedido = Pedido(
            id_produto=prod_id,
            id_cliente=cli_id,
            peso=peso,
            valor_total=valor_total
        )

        db.session.add(novo_pedido)
        db.session.commit()

        app.logger.info(
            f"Pedido registrado: {peso}kg de {produto.nome} - "
            f"Cliente: {cliente.nome} - Valor: R$ {valor_total}"
        )
        flash("Pedido registrado com sucesso!", "success")

    except Exception as e:
        db.session.rollback()
        app.logger.error(
            f"Erro ao processar pedido: {e}\n{traceback.format_exc()}"
        )
        flash("Erro ao processar transação.", "danger")

    return redirect(url_for('estoque'))


@app.route('/financeiro')
@login_required
@roles_accepted('ADMIN', 'DONO', 'GERENTE')
def financeiro():
    try:
        receber = Cliente.query.filter(Cliente.saldo < 0).all()
        gastos = Financeiro.query.order_by(
            Financeiro.data_registro.desc()
        ).all()

        return render_template(
            'financeiro.html',
            receber=receber,
            gastos=gastos
        )
    except Exception as e:
        app.logger.error(
            f"Erro no financeiro: {e}\n{traceback.format_exc()}"
        )
        flash("Erro ao carregar dados financeiros.", "danger")
        return redirect(url_for('dashboard'))


@app.route('/registrar_pagamento', methods=['POST'])
@login_required
@roles_accepted('ADMIN', 'DONO', 'GERENTE')
def registrar_pagamento():
    try:
        cli_id = int(request.form.get('id_cliente'))
        valor = float(request.form.get('valor_pagamento'))

        if valor <= 0:
            flash(
                "Valor do pagamento deve ser maior que zero!",
                "danger"
            )
            return redirect(url_for('financeiro'))

        cliente = Cliente.query.get(cli_id)
        if not cliente:
            flash("Cliente não encontrado.", "danger")
            return redirect(url_for('financeiro'))

        cliente.saldo += valor

        novo_gasto = Financeiro(
            descricao=f"Pagamento recebido de: {cliente.nome}",
            valor=valor,
            tipo='Entrada'
        )

        db.session.add(novo_gasto)
        db.session.commit()

        app.logger.info(
            f"Pagamento registrado: R$ {valor} - Cliente: {cliente.nome}"
        )
        flash(
            "Pagamento registrado e saldo atualizado!",
            "success"
        )

    except Exception as e:
        db.session.rollback()
        app.logger.error(
            f"Erro ao registrar pagamento: {e}\n{traceback.format_exc()}"
        )
        flash("Erro ao processar pagamento.", "danger")

    return redirect(url_for('financeiro'))


@app.route('/admin/logs')
@login_required
@roles_accepted('ADMIN')
def visualizar_logs():
    path = 'logs/manuela_metais.log'

    if os.path.exists(path):
        with open(path, 'r') as f:
            logs = f.readlines()[-100:]
    else:
        logs = []

    return render_template(
        'admin_logs.html',
        logs=reversed(logs)
    )
