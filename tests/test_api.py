import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_healthz():
    response = client.get('/v1/score/healthz')
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict():
    payload = {"features": [0.1, 0.2, 0.3, 0.4]}
    response = client.post('/v1/score/predict', json=payload)
    assert response.status_code == 200
    assert 'score' in response.json()
    assert isinstance(response.json()['score'], float)
