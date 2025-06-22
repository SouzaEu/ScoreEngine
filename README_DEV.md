# Guia de Execução e Contribuição para Desenvolvedores

Este documento tem como objetivo orientar desenvolvedores sobre como rodar o ScoreEngine localmente e como contribuir de forma eficiente e padronizada com o projeto.

---

## 1. Como rodar o projeto localmente

### Pré-requisitos
- Python 3.9+
- Docker e Docker Compose
- Git

### Passos para execução

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/nSevenCo/ScoreEngine.git
   cd ScoreEngine
   ```

2. **Configure as variáveis de ambiente:**
   ```bash
   cp env_vars.txt .env
   # Edite o arquivo .env conforme sua infraestrutura local
   ```

3. **Inicialize o ambiente:**
   ```bash
   ./init.sh
   ```
   Esse script irá:
   - Criar o ambiente virtual Python
   - Instalar as dependências
   - Inicializar o banco de dados
   - Treinar o modelo inicial
   - Subir os serviços via Docker Compose

4. **Acesse os serviços:**
   - API: http://localhost:8000
   - MLflow: http://localhost:5000
   - Grafana: http://localhost:3000
   - Prometheus: http://localhost:9090

### Comandos úteis
- **Executar validação estatística das features:**
  ```bash
  python scripts/validate_feature_stats.py --sample_size 1000 --out print
  ```
- **Treinar modelo manualmente:**
  ```bash
  python -m app.ml.train_model
  ```

---

## 2. Como contribuir

### Fluxo de contribuição
1. Realize um fork deste repositório
2. Crie uma branch para sua feature ou correção:
   ```bash
   git checkout -b minha-feature
   ```
3. Faça commits claros e objetivos, seguindo boas práticas de mensagem
4. Garanta que os testes estejam passando e que o projeto rode localmente
5. Abra um Pull Request detalhado, explicando sua contribuição

### Boas práticas
- Siga o padrão de código PEP8
- Documente funções, classes e endpoints
- Prefira testes automatizados sempre que possível
- Mantenha o código limpo e modular
- Sugestões de novas features ou melhorias podem ser abertas via Issues

### Rodando testes
- (Adicione aqui instruções de testes automatizados, caso existam)

---

## Dúvidas ou problemas?
Abra uma Issue no repositório ou entre em contato com o time responsável. 