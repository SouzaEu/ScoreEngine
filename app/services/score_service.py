from typing import List
import logging
from ..core.ml_model import MLModel

logger = logging.getLogger(__name__)

class ScoreService:
    def __init__(self):
        self.model = MLModel()
        logger.info("ScoreService initialized")

    def predict_score(self, features: List[float]) -> float:
        logger.info("Predicting score for features=%s", features)
        clean_features = [float(x) for x in features]
        score = float(self.model.predict(clean_features))
        logger.info("Predicted score=%.4f", score)
        return score
