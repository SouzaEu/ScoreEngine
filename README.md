# ScoreEngine

ScoreEngine é um microserviço robusto para cálculo, versionamento e fornecimento de scores de reputação transacional de usuários, utilizando dados comportamentais recebidos em tempo real via integração com parceiros. Projetado para ambientes de alta escala e compliance, é ideal para fintechs, marketplaces e plataformas que demandam análise de risco automatizada.

---

## Funcionalidades

- Cálculo de score de reputação em tempo real
- Versionamento e gerenciamento de modelos de Machine Learning
- Pipeline de features comportamentais com validação estatística
- Cache inteligente com Redis
- Logging estruturado e compliance LGPD
- Explicabilidade de scores (SHAP)
- Sistema de contestação de score
- Monitoramento com Prometheus e Grafana
- Integração com MLflow para rastreabilidade de experimentos
- Pronto para integração com EventPipeline (Kafka)

---

## Stack Tecnológica

- FastAPI + Uvicorn (API)
- Redis (cache de features e scores)
- PostgreSQL (persistência e logs)
- MLflow (versionamento de modelos)
- Prometheus + Grafana (monitoramento)
- Kafka (eventos comportamentais)
- Docker + Docker Compose (deploy)

---

## Documentação para Desenvolvedores

Para instruções detalhadas de instalação, execução local e contribuição, consulte o arquivo [README_DEV.md](./README_DEV.md).

---

## Licença

Distribuído sob a Licença MIT. Veja o arquivo [LICENSE](./LICENSE) para mais detalhes.