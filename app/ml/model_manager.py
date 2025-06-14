from typing import Dict, Any, Optional
import mlflow
import joblib
from datetime import datetime
from pathlib import Path
from app.core.logger import setup_logger

logger = setup_logger('model_manager')

class ModelManager:
    """
    Gerenciador de modelos ML com versionamento
    """
    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        self.current_model = None
        self.current_version = None
        self._load_latest_model()

    def _load_latest_model(self) -> None:
        """
        Carrega o modelo mais recente
        """
        try:
            model_files = list(self.model_dir.glob("model_*.pkl"))
            if not model_files:
                logger.warning("Nenhum modelo encontrado")
                return

            latest_model = max(model_files, key=lambda x: x.stat().st_mtime)
            self.current_model = joblib.load(latest_model)
            self.current_version = latest_model.stem.split("_")[1]
            logger.info(f"Modelo carregado: {self.current_version}")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {str(e)}")
            raise

    def load_model_version(self, version: str) -> None:
        """
        Carrega uma versão específica do modelo
        """
        model_path = self.model_dir / f"model_{version}.pkl"
        if not model_path.exists():
            raise ValueError(f"Modelo versão {version} não encontrado")

        self.current_model = joblib.load(model_path)
        self.current_version = version
        logger.info(f"Modelo versão {version} carregado")

    def save_model(self, model: Any, version: str) -> None:
        """
        Salva uma nova versão do modelo
        """
        model_path = self.model_dir / f"model_{version}.pkl"
        joblib.dump(model, model_path)
        
        # Registra no MLflow
        with mlflow.start_run():
            mlflow.log_param("version", version)
            mlflow.log_param("timestamp", datetime.utcnow().isoformat())
            mlflow.log_artifact(str(model_path))
        
        logger.info(f"Modelo versão {version} salvo")

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza predição com o modelo atual
        """
        if not self.current_model:
            raise ValueError("Nenhum modelo carregado")

        try:
            prediction = self.current_model.predict_proba([list(features.values())])[0]
            return {
                "score": float(prediction[1] * 100),
                "version": self.current_version,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro na predição: {str(e)}")
            raise

    def get_model_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o modelo atual
        """
        return {
            "version": self.current_version,
            "features": self.current_model.feature_names_in_.tolist() if hasattr(self.current_model, 'feature_names_in_') else [],
            "last_updated": datetime.fromtimestamp(self.model_dir.stat().st_mtime).isoformat()
        } 