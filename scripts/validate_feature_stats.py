import argparse
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from app.core.config import settings
from app.db.session import SessionLocal
from scipy.stats import spearmanr, pearsonr
import mlflow
import os

# Argumentos de linha de comando
parser = argparse.ArgumentParser(description="Validação estatística das features comportamentais.")
parser.add_argument('--sample_size', type=int, default=10000, help='Tamanho da amostra')
parser.add_argument('--out', type=str, default='print', choices=['print', 'csv', 'mlflow', 'all'], help='Destino do resultado')
parser.add_argument('--days', type=int, default=30, help='Dias retroativos para buscar dados')
args = parser.parse_args()

# Conexão com o banco
engine = create_engine(settings.DATABASE_URL)

# Consulta SQL
with engine.connect() as conn:
    # Descobre colunas de features automaticamente
    result = conn.execute("SELECT * FROM user_features LIMIT 1")
    columns = result.keys()
    feature_columns = [c for c in columns if c not in ('id', 'user_id', 'last_updated', 'score') and c != 'feature_data']
    # Busca dados
    query = f"""
        SELECT user_id, feature_data, last_updated
        FROM user_features
        WHERE last_updated > NOW() - interval '{args.days} days'
        LIMIT {args.sample_size}
    """
    df = pd.read_sql(query, conn)

# Expande o JSON de features
features_df = pd.json_normalize(df['feature_data'])
if 'score' in df.columns:
    features_df['score'] = df['score']
else:
    # Tenta buscar score da tabela de scores
    with engine.connect() as conn:
        scores = pd.read_sql(f"SELECT user_id, score FROM scores WHERE timestamp > NOW() - interval '{args.days} days'", conn)
    features_df = features_df.join(df['user_id'])
    features_df = features_df.merge(scores, on='user_id', how='left')

# Remove colunas não numéricas
num_features = features_df.select_dtypes(include=[np.number]).columns.tolist()
num_features = [f for f in num_features if f != 'score']

# Calcula correlação
results = []
for feature in num_features:
    pearson_corr, pearson_p = pearsonr(features_df[feature], features_df['score'])
    spearman_corr, spearman_p = spearmanr(features_df[feature], features_df['score'])
    results.append({
        'feature': feature,
        'pearson_corr': pearson_corr,
        'pearson_p': pearson_p,
        'spearman_corr': spearman_corr,
        'spearman_p': spearman_p
    })

results_df = pd.DataFrame(results)

# Saídas
if args.out in ('print', 'all'):
    print("Correlação das features com o score:")
    print(results_df.sort_values('spearman_corr', key=abs, ascending=False))
if args.out in ('csv', 'all'):
    results_df.to_csv('feature_score_correlation.csv', index=False)
    print("Arquivo CSV salvo: feature_score_correlation.csv")
if args.out in ('mlflow', 'all'):
    mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(settings.MLFLOW_EXPERIMENT_NAME)
    with mlflow.start_run(run_name="feature_stats_validation"):
        mlflow.log_artifact('feature_score_correlation.csv')
        mlflow.log_param('sample_size', args.sample_size)
        mlflow.log_param('days', args.days)
        print("Resultado logado no MLflow.") 