# ScoreEngine

## Descrição

Microserviço responsável por calcular, versionar e servir a pontuação de reputação transacional de um usuário, a partir de dados comportamentais recebidos por parceiros integrados via API.

## Funcionalidades

- Cálculo de score de reputação em tempo real
- Versionamento de modelos ML
- Cache inteligente com Redis
- Logging estruturado para LGPD
- Explicabilidade de scores
- Sistema de contestação
- Monitoramento com Prometheus
- Integração com MLflow

## Stack Tecnológica

- FastAPI + Uvicorn
- Redis (cache)
- PostgreSQL (logs)
- MLflow (versionamento de modelos)
- Prometheus + Grafana (monitoramento)
- Docker + Docker Compose

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/Lynexhq/ScoreEngine
cd ScoreEngine
```

2. Configure as variáveis de ambiente:
```bash
cp env_vars.txt .env
# Edite o arquivo .env com as configurações do Render
```

3. Inicie os serviços:
```bash
docker-compose up -d
```

## Deploy no Render

1. Crie um novo Web Service no Render
2. Conecte com o repositório
3. Configure as variáveis de ambiente do arquivo env_vars.txt
4. Use o comando de build: `docker-compose up -d`
5. Configure o Redis e PostgreSQL como serviços externos no Render

## API

### POST /api/v1/scores/calculate

Calcula o score de reputação para um usuário.

**Request:**
```json
{
  "user_id": "abc123",
  "features": {
    "pagou_pix": true,
    "entregas_atrasadas": 2,
    "chargebacks": 1,
    "dias_inativo": 12,
    "rating_medio": 4.3
  },
  "source_app": "AppX",
  "model_version": "v1.2.3"
}
```

**Response:**
```json
{
  "user_id": "abc123",
  "score": 38,
  "risk": "alto",
  "explanation": [
    {
      "feature": "chargebacks",
      "impact": -20,
      "description": "chargeback recente"
    }
  ],
  "features_used": ["pagou_pix", "entregas_atrasadas", "chargebacks"],
  "model_version": "v1.2.3",
  "timestamp": "2024-03-14T18:12:00Z"
}
```

### Endpoints Adicionais

- GET /api/v1/scores/history/{user_id}
- POST /api/v1/scores/contest/{user_id}
- GET /api/v1/scores/model/info

## Segurança

- Autenticação via JWT
- Logs estruturados para LGPD
- Cache com TTL
- Validação de features
- Rate limiting

## Monitoramento

- Métricas Prometheus
- Logs estruturados
- Rastreabilidade de scores
- Alertas configuráveis 
