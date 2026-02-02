import secrets
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (se existir)
load_dotenv()

class Config:
    """
    Configurações da aplicação Flask.
    Em produção, todas as variáveis devem vir do ambiente (.env ou variáveis de sistema).
    """
    
    # Segurança
    SECRET_KEY = os.getenv('SECRET_KEY') or secrets.token_hex(32)
    
    # Banco de Dados
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'manuela_metais')
    
    # URI completa do SQLAlchemy
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    PERMANENT_SESSION_LIFETIME = 7200  # 2 horas em segundos
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'  # HTTPS obrigatório em produção
    SESSION_COOKIE_HTTPONLY = True  # Previne XSS
    SESSION_COOKIE_SAMESITE = 'Lax'  # Previne CSRF
    
    # CSRF
    WTF_CSRF_TIME_LIMIT = None  # Token não expira (ou defina em segundos)
    WTF_CSRF_SSL_STRICT = os.getenv('FLASK_ENV') == 'production'