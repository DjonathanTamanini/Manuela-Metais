import mysql.connector
from flask import current_app

def get_conexao():
    # Se estiver usando a classe Config, acesse assim:
    return mysql.connector.connect(
        host=current_app.config.get('MYSQL_HOST', 'localhost'),
        user=current_app.config.get('MYSQL_USER', 'root'),
        password=current_app.config.get('MYSQL_PASSWORD', ''),
        database=current_app.config.get('MYSQL_DB') # Verifique se não está MYSQL_DATABASE aqui
    )