from flask import Flask, jsonify
import os
from dotenv import load_dotenv
from celery import Celery
from database import engine, Base, SessionLocal
from scan import scan_site

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do Flask
app = Flask(__name__)

# Configuração do Celery
celery_app = Celery(
    "tasks",
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL")
)

# Criar tabelas do banco de dados
Base.metadata.create_all(bind=engine)

# Endpoint de saúde
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "API Checkro rodando no Azure!"}), 200

# Função para iniciar a API
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
