import mlflow
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score
import shap
import matplotlib.pyplot as plt

from app.core.config import settings

def generate_synthetic_data(n_samples=1000):
    """
    Gera dados sintéticos para treinamento inicial
    """
    np.random.seed(42)
    
    data = {
        'pix_volume': np.random.normal(1000, 500, n_samples),
        'avg_transaction_value': np.random.normal(100, 50, n_samples),
        'transaction_frequency': np.random.normal(10, 5, n_samples),
        'chargeback_rate': np.random.normal(0.01, 0.005, n_samples),
        'app_connections': np.random.normal(3, 1, n_samples),
        'account_age_days': np.random.normal(180, 90, n_samples)
    }
    
    # Gera o target (score) com alguma lógica de negócio
    base_score = 50
    score = (
        base_score +
        data['pix_volume'] * 0.01 +
        data['avg_transaction_value'] * 0.1 +
        data['transaction_frequency'] * 2 +
        (1 - data['chargeback_rate'] * 100) * 10 +
        data['app_connections'] * 5 +
        data['account_age_days'] * 0.05
    )
    
    # Adiciona ruído
    score += np.random.normal(0, 5, n_samples)
    
    # Normaliza para 0-100
    score = (score - score.min()) / (score.max() - score.min()) * 100
    
    data['score'] = score
    
    return pd.DataFrame(data)

def train_model():
    """
    Treina o modelo inicial e registra no MLflow
    """
    # Configura o MLflow
    mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(settings.MLFLOW_EXPERIMENT_NAME)
    
    # Gera dados sintéticos
    df = generate_synthetic_data()
    
    # Separa features e target
    X = df.drop('score', axis=1)
    y = df['score']
    
    # Divide em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Normaliza as features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Inicia o run do MLflow
    with mlflow.start_run():
        # Treina o modelo
        model = XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        model.fit(X_train_scaled, y_train)
        
        # Faz previsões
        y_pred = model.predict(X_test_scaled)
        
        # Calcula métricas
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Registra métricas
        mlflow.log_metric("mse", mse)
        mlflow.log_metric("r2", r2)
        
        # Registra o modelo
        mlflow.xgboost.log_model(model, "model")
        
        # Registra o scaler
        mlflow.sklearn.log_model(scaler, "scaler")
        
        # Gera e registra explicação SHAP
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test_scaled)
        
        # Plota e salva o gráfico SHAP
        shap.summary_plot(
            shap_values,
            X_test,
            show=False,
            plot_size=(10, 6)
        )
        mlflow.log_figure(plt.gcf(), "shap_summary.png")
        
        print(f"Modelo treinado e registrado com sucesso!")
        print(f"MSE: {mse:.2f}")
        print(f"R2: {r2:.2f}")

if __name__ == "__main__":
    train_model() 