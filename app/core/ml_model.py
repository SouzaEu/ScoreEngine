import joblib
import logging
from .config import get_settings
from pathlib import Path

logger = logging.getLogger(__name__)

class MLModel:
    def __init__(self):
        settings = get_settings()
        self.model_path = Path(settings.model_path)
        self.model = None

    def load_model(self):
        if self.model is None:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            logger.info("Loading model from %s", self.model_path)
            self.model = joblib.load(self.model_path)
            logger.info("Model loaded")
        return self.model

    def predict(self, features):
        model = self.load_model()
        if hasattr(model, "predict_proba"):
            score = model.predict_proba([features])[0][1]
        else:
            score = float(model.predict([features])[0])
        logger.info("Model prediction=%.4f", score)
        return score
