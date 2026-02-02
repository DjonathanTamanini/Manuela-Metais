# ⚙️ Manuela Metais — Sistema de Gestão

🚀 **Sistema Web de Gestão Empresarial** | 🐍 Python + Flask | 🗄️ MySQL  
Para controle de vendas, estoque, clientes, fornecedores e financeiro.

---

## 📌 Sobre o Projeto

O **Manuela Metais** é um sistema web desenvolvido para auxiliar na gestão administrativa e operacional de empresas do ramo de metais/comércio. Ele centraliza informações e processos essenciais, proporcionando maior organização, controle e tomada de decisão.

O sistema foi construído com **Flask (Python)** no back-end, templates em **HTML + Jinja**, estilização em **CSS**, e persistência de dados em **MySQL**.

---

## 🎯 Funcionalidades Principais

- Autenticação de usuários (Login)
- Controle de usuários (Admin)
- Dashboard gerencial
- Cadastro e edição de clientes, fornecedores, produtos e usuários
- Controle de estoque, vendas e financeiro
- Registro de logs em arquivo (`manuela_metais.log`)
- Arquitetura organizada em MVC

---

## 🛠️ Tecnologias Utilizadas

- Python
- Flask
- MySQL
- HTML/CSS
- Jinja2
- python-dotenv

---

## ⚙️ Instalação

1. Clone o repositório:
```bash
git clone https://github.com/SEU_USUARIO/Manuela-Metais.git
cd Manuela-Metais
```

2. Crie e ative o ambiente virtual:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure o arquivo `.env`:
```
SECRET_KEY=sua_chave_secreta
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha
MYSQL_DB=manuela_metais
```

5. Crie o banco de dados:
```sql
CREATE DATABASE manuela_metais;
```

6. Execute o sistema:
```bash
python run.py
```
Acesse em: http://127.0.0.1:5000

---

## 📄 Licença

Este projeto está sob a licença MIT.
