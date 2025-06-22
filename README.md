# ScoreEngine

ScoreEngine é um microserviço para cálculo, versionamento e fornecimento de scores de reputação transacional de usuários, utilizando dados comportamentais em tempo real. Ideal para fintechs, marketplaces e plataformas que demandam análise de risco automatizada.

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

## Documentação

- [Guia de Contribuição](./CONTRIBUTING.md)
- [Changelog](./CHANGELOG.md)
- [Código de Conduta](./CODE_OF_CONDUCT.md)

---

## Licença

Distribuído sob a Licença MIT. Veja o arquivo [LICENSE](./LICENSE) para mais detalhes.