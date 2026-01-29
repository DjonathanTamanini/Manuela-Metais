# MANUELA METAIS - Sistema de Gestão

Sistema completo para gestão de empresa de coleta de metais recicláveis.

## ⚠️ AVISOS CRÍTICOS (LEIA ANTES DE USAR)

### O que este sistema NÃO TEM (e você vai precisar):

1. **Autenticação/Login** - Qualquer pessoa com acesso pode ver e modificar tudo
2. **Controle de permissões** - Não há diferença entre admin/funcionário/visualizador
3. **Backup automático** - Se o arquivo data.json corromper, você perde TUDO
4. **Validações de negócio robustas**:
   - Não impede deletar cliente com saldo devedor
   - Não impede vender sem estoque
   - Não valida CPF/CNPJ
   - Não impede valores negativos em lugares incorretos
5. **Relatórios** - Não há dashboard financeiro, gráficos, exportação para Excel
6. **Histórico/Auditoria** - Não rastreia quem fez o quê e quando
7. **Integração bancária** - Sem conciliação automática
8. **Notas fiscais** - Sem emissão ou importação
9. **Multi-empresa** - Só funciona para UMA empresa
10. **Performance** - Com 10.000+ registros vai ficar lento

### O que vai dar problema:

- **Perda de dados**: Um único erro no JSON e você perde tudo
- **Concorrência**: Se 2 pessoas usarem ao mesmo tempo, dados podem ser sobrescritos
- **Escalabilidade**: Não aguenta crescimento real do negócio
- **Manutenção**: Cada nova feature vai exigir alterar múltiplos arquivos
- **Segurança**: Vulnerável a diversos ataques (XSS, CSRF, SQL injection se migrar para BD)

## 🚀 Como Usar

### 1. Instalar dependências:
```bash
pip install -r requirements.txt
```

### 2. Rodar o sistema:
```bash
python app.py
```

### 3. Acessar no navegador:
```
http://localhost:5000
```

## 📋 Funcionalidades

### ✅ Implementado:
- Cadastro de clientes (com sistema de saldo)
- Cadastro de fornecedores
- Cadastro de funcionários
- Cadastro de produtos (tipos de metais)
- Controle de estoque (entrada/saída)
- Contas a receber (com negativação e adiantamento)
- Contas a pagar
- Controle de gastos
- Pedidos de compra

### ❌ Faltando (e você VAI PRECISAR):
- Autenticação e segurança
- Relatórios financeiros
- Dashboard com gráficos
- Backup automático
- Histórico de alterações
- Impressão de comprovantes
- Integração com email/WhatsApp
- App mobile
- Multi-usuário com permissões
- Banco de dados real (PostgreSQL/MySQL)

## 🎯 Como funciona a NEGATIVAÇÃO/ADIANTAMENTO:

### Venda (Cliente fica negativado):
1. Vá em "Contas a Receber"
2. Clique em "Registrar Venda"
3. Escolha o cliente e valor
4. O saldo do cliente fica NEGATIVO (ele deve)

### Pagamento/Adiantamento:
1. Vá em "Contas a Receber"
2. Clique em "Receber Pagamento/Adiantamento"
3. Escolha o cliente e valor
4. O saldo do cliente aumenta (pode ficar POSITIVO = crédito)

### Exemplo prático:
- Cliente João tem saldo R$ 0,00
- Você vende R$ 100,00 → Saldo vira -R$ 100,00 (negativado)
- João paga R$ 150,00 → Saldo vira +R$ 50,00 (crédito/adiantamento)
- Próxima venda de R$ 30,00 → Saldo vira +R$ 20,00 (ainda tem crédito)

## 📁 Estrutura de Arquivos

```
.
├── app.py                      # Backend Flask
├── data.json                   # "Banco de dados" (arquivo JSON)
├── requirements.txt            # Dependências Python
├── templates/                  # Templates HTML
│   ├── index.html
│   ├── clientes.html
│   ├── fornecedores.html
│   ├── funcionarios.html
│   ├── produtos.html
│   ├── estoque.html
│   ├── contas_receber.html
│   ├── contas_pagar.html
│   ├── gastos.html
│   └── pedidos_compra.html
└── static/
    ├── css/
    │   └── style.css           # Estilos
    └── js/
        ├── clientes.js
        └── contas_receber.js
```

## ⚡ Próximos Passos OBRIGATÓRIOS:

### Curto Prazo (Semana 1):
1. **BACKUP MANUAL DIÁRIO** - Copie data.json todo dia
2. **Teste tudo** - Simule todos os fluxos antes de usar com dados reais
3. **Documente suas regras** - Escreva o processo manual no papel

### Médio Prazo (Mês 1):
1. Implementar autenticação básica
2. Migrar para banco de dados real (SQLite mínimo)
3. Adicionar validações críticas
4. Criar rotina de backup automático

### Longo Prazo (Mês 3+):
1. Contratar desenvolvedor para refatorar
2. Ou migrar para sistema pronto (ERP comercial)
3. Adicionar relatórios e dashboard
4. Implementar permissões de usuário

## 🔴 REALIDADE DURA:

Este sistema foi feito em algumas horas. Um sistema ERP profissional leva **6-12 meses** de desenvolvimento e custa **R$ 50.000 - R$ 500.000**.

**Você tem 3 opções:**

1. **Usar sistema pronto** (R$ 200-500/mês) - Recomendado
   - Exemplos: Omie, Bling, Tiny ERP, ContaAzul

2. **Este sistema + investir em melhorias** (R$ 10.000-30.000)
   - Contratar dev por 2-3 meses para profissionalizar

3. **Usar do jeito que está e rezar** (Grátis mas arriscado)
   - Faça backup manual TODO DIA
   - Aceite que vai dar problema
   - Tenha plano B no papel

## 💡 Recomendação Final:

Se seu negócio movimenta mais de R$ 50k/mês, **NÃO USE ESTE SISTEMA EM PRODUÇÃO**.

Use um ERP comercial ou invista em desenvolvimento profissional.

Este código serve para:
- Prototipar ideias
- Entender o fluxo do negócio
- Testar se vale a pena um sistema maior
- Base para contratar desenvolvedor que entenda o que você precisa

**Não serve para:**
- Rodar empresa real sem supervisão constante
- Confiar como única fonte de dados
- Escalar o negócio