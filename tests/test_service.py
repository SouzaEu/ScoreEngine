import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.score_service import ScoreService


def test_service_predict():
    service = ScoreService()
    score = service.predict_score([0.1, 0.2, 0.3, 0.4])
    assert isinstance(score, float)
