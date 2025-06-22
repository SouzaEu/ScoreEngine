import pytest
from app.services.feature_service import FeatureService


def test_feature_service_instancia():
    try:
        service = FeatureService()
    except Exception as e:
        pytest.fail(f"Falha ao instanciar FeatureService: {e}") 