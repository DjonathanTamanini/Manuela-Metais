from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
import logging
from logging.handlers import RotatingFileHandler
import os

# Inicialização das extensões
db = SQLAlchemy()
bcrypt = Bcrypt()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    
    # USAR CONFIG.PY (não .env diretamente)
    from config import Config
    app.config.from_object(Config)
    
    # Inicializar extensões
    db.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    # Configuração de Logs
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler(
        'logs/manuela_metais.log',
        maxBytes=1024 * 1024,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

    with app.app_context():
        from .controllers import routes
        db.create_all()
        return app