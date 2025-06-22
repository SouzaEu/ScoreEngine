from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram
import time
from typing import Dict, Any

from app.core.config import settings
from app.api.v1.endpoints import scores, features, models
from app.core.middleware import PrometheusMiddleware

app = FastAPI(
    title="Score Engine N7",
    description="API de reputação preditiva transacional em tempo real",
    version="1.0.0"
)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware do Prometheus
app.add_middleware(PrometheusMiddleware)

# Rotas da API
app.include_router(scores.router, prefix="/api/v1/scores", tags=["scores"])
app.include_router(features.router, prefix="/api/v1/features", tags=["features"])
app.include_router(models.router, prefix="/api/v1/models", tags=["models"])

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Endpoint de verificação de saúde da API
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    ) 