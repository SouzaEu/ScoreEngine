from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    model_path: str = "model/xgboost_model.pkl"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
