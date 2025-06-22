import pytest
from app.services.score_service import ScoreService


def test_score_service_instancia():
    try:
        service = ScoreService()
    except Exception as e:
        pytest.fail(f"Falha ao instanciar ScoreService: {e}") 