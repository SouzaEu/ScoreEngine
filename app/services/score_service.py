import mlflow
import shap
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Tuple
import pandas as pd
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.score import Score
from app.models.score_contest import ScoreContest

class ScoreService:
    def __init__(self):
        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        self.model = self._load_model()
        self.explainer = self._create_explainer()
    
    def _load_model(self):
        """
        Carrega o modelo mais recente do MLflow
        """
        client = mlflow.tracking.MlflowClient()
        experiment = client.get_experiment_by_name(settings.MLFLOW_EXPERIMENT_NAME)
        
        if not experiment:
            raise Exception("Experimento MLflow não encontrado")
        
        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            filter_string="metrics.accuracy > 0.7",
            order_by=["metrics.accuracy DESC"]
        )
        
        if not runs:
            raise Exception("Nenhum modelo válido encontrado")
        
        best_run = runs[0]
        return mlflow.pyfunc.load_model(f"runs:/{best_run.info.run_id}/model")
    
    def _create_explainer(self):
        """
        Cria o explicador SHAP para o modelo
        """
        # Usa um conjunto de dados de exemplo para treinar o explicador
        background_data = pd.DataFrame({
            'pix_volume': np.random.normal(1000, 500, 1000),
            'avg_transaction_value': np.random.normal(100, 50, 1000),
            'transaction_frequency': np.random.normal(10, 5, 1000),
            'chargeback_rate': np.random.normal(0.01, 0.005, 1000),
            'app_connections': np.random.normal(3, 1, 1000)
        })
        
        return shap.TreeExplainer(self.model, background_data)
    
    async def calculate_score(
        self,
        user_id: str,
        features: Dict[str, Any]
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Calcula o score e gera explicação usando SHAP
        """
        # Converte features para DataFrame
        feature_df = pd.DataFrame([features])
        
        # Calcula o score
        score = float(self.model.predict(feature_df)[0])
        
        # Gera explicação SHAP
        shap_values = self.explainer.shap_values(feature_df)
        
        # Formata a explicação
        explanation = []
        for feature, value, shap_value in zip(
            feature_df.columns,
            feature_df.iloc[0],
            shap_values[0]
        ):
            explanation.append({
                "feature": feature,
                "value": float(value),
                "impact": float(shap_value),
                "description": self._get_feature_description(feature, value, shap_value)
            })
        
        # Salva o score no banco
        await self._save_score(user_id, score, features, explanation)
        
        return score, explanation
    
    def _get_feature_description(
        self,
        feature: str,
        value: float,
        impact: float
    ) -> str:
        """
        Gera uma descrição legível do impacto de uma feature
        """
        impact_direction = "aumentou" if impact > 0 else "diminuiu"
        impact_magnitude = "significativamente" if abs(impact) > 0.1 else "levemente"
        
        return f"O valor de {feature} ({value:.2f}) {impact_direction} {impact_magnitude} o score"
    
    async def _save_score(
        self,
        user_id: str,
        score: float,
        features: Dict[str, Any],
        explanation: List[Dict[str, Any]]
    ):
        """
        Salva o score e sua explicação no banco de dados
        """
        db = next(get_db())
        score_record = Score(
            user_id=user_id,
            score=score,
            features=features,
            explanation=explanation,
            timestamp=datetime.utcnow()
        )
        db.add(score_record)
        db.commit()
    
    async def get_score_history(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retorna o histórico de scores de um usuário
        """
        db = next(get_db())
        scores = db.query(Score).filter(
            Score.user_id == user_id
        ).order_by(Score.timestamp.desc()).all()
        
        return [
            {
                "score": score.score,
                "timestamp": score.timestamp.isoformat(),
                "features": score.features,
                "explanation": score.explanation
            }
            for score in scores
        ]
    
    async def contest_score(self, user_id: str, reason: str) -> Dict[str, Any]:
        """
        Registra uma contestação de score
        """
        db = next(get_db())
        contest = ScoreContest(
            user_id=user_id,
            reason=reason,
            timestamp=datetime.utcnow()
        )
        db.add(contest)
        db.commit()
        
        return {
            "status": "success",
            "message": "Contestação registrada com sucesso",
            "contest_id": contest.id
        }
    
    def get_current_timestamp(self) -> str:
        """
        Retorna o timestamp atual em formato ISO
        """
        return datetime.utcnow().isoformat() 