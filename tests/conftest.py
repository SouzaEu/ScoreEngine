import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pathlib
import pytest

from scripts.train_model import main as train_model_main

@pytest.fixture(scope="session", autouse=True)
def ensure_model():
    model_path = pathlib.Path("model/xgboost_model.pkl")
    if not model_path.exists():
        train_model_main()

