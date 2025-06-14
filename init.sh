#!/bin/bash

# Cria ambiente virtual
python -m venv venv
source venv/bin/activate

# Instala dependências
pip install -r requirements.txt

# Inicializa o banco de dados
python -m app.db.init_db

# Treina o modelo inicial
python -m app.ml.train_model

# Inicia os serviços com Docker Compose
docker-compose up -d

echo "Ambiente inicializado com sucesso!"
echo "API disponível em: http://localhost:8000"
echo "MLflow disponível em: http://localhost:5000"
echo "Grafana disponível em: http://localhost:3000"
echo "Prometheus disponível em: http://localhost:9090" 