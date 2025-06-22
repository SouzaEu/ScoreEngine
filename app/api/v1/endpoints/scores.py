from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.config import settings
from app.services.score_service import ScoreService
from app.services.feature_service import FeatureService
from app.core.security import get_current_user
from app.core.cache import cache_score
from app.core.logger import ScoreLogger
from app.ml.model_manager import ModelManager

router = APIRouter()
score_service = ScoreService()
feature_service = FeatureService()
model_manager = ModelManager()
score_logger = ScoreLogger()

class ScoreRequest(BaseModel):
    user_id: str = Field(..., description="ID único do usuário")
    features: Dict[str, Any] = Field(..., description="Features comportamentais do usuário")
    source_app: str = Field(..., description="Aplicação de origem da requisição")
    model_version: str = Field(None, description="Versão específica do modelo (opcional)")

class ScoreResponse(BaseModel):
    user_id: str
    score: float
    risk: str
    explanation: List[Dict[str, Any]]
    features_used: List[str]
    model_version: str
    timestamp: str

@router.post("/calculate", response_model=ScoreResponse)
@cache_score(expire=3600)  # Cache por 1 hora
async def calculate_score(
    request: ScoreRequest,
    current_user: Dict = Depends(get_current_user),
    fastapi_request: Request = None
) -> ScoreResponse:
    """
    Calcula o score de reputação para um usuário
    
    - **user_id**: ID único do usuário
    - **features**: Features comportamentais (ex: pagou_pix, entregas_atrasadas)
    - **source_app**: Aplicação de origem
    - **model_version**: Versão específica do modelo (opcional)
    """
    try:
        # Carrega versão específica do modelo se solicitado
        if request.model_version:
            model_manager.load_model_version(request.model_version)
        
        # Obtém features do usuário
        user_features = await feature_service.get_user_features(request.user_id)
        
        # Combina features
        combined_features = {**user_features, **request.features}
        
        # Calcula o score
        prediction = model_manager.predict(combined_features)
        
        # Gera explicação
        explanation = await score_service.generate_explanation(
            features=combined_features,
            score=prediction["score"]
        )
        
        # Determina nível de risco
        risk = "alto" if prediction["score"] < 40 else "médio" if prediction["score"] < 70 else "baixo"
        
        # Registra log LGPD
        trace_id = fastapi_request.state.trace_id if fastapi_request else None
        score_logger.log_score_calculation(
            user_id=request.user_id,
            score=prediction["score"],
            features=combined_features,
            model_version=prediction["version"],
            source_app=request.source_app,
            explanation=explanation,
            trace_id=trace_id
        )
        
        return ScoreResponse(
            user_id=request.user_id,
            score=prediction["score"],
            risk=risk,
            explanation=explanation,
            features_used=list(combined_features.keys()),
            model_version=prediction["version"],
            timestamp=prediction["timestamp"]
        )
    
    except Exception as e:
        # Fallback: buscar último score salvo
        last_scores = await score_service.get_score_history(request.user_id)
        if last_scores:
            last_score = last_scores[0]
            return ScoreResponse(
                user_id=request.user_id,
                score=last_score["score"],
                risk="desconhecido",
                explanation=last_score["explanation"],
                features_used=list(last_score["features"].keys()),
                model_version="desconhecido",
                timestamp=last_score["timestamp"]
            )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{user_id}")
async def get_score_history(
    user_id: str,
    current_user: Dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Retorna o histórico de scores de um usuário
    """
    try:
        return await score_service.get_score_history(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/contest/{user_id}")
async def contest_score(
    user_id: str,
    reason: str,
    current_user: Dict = Depends(get_current_user),
    fastapi_request: Request = None
) -> Dict[str, Any]:
    """
    Permite que um usuário conteste seu score
    """
    try:
        result = await score_service.contest_score(user_id, reason)
        trace_id = fastapi_request.state.trace_id if fastapi_request else None
        score_logger.log_score_contest(
            user_id=user_id,
            reason=reason,
            original_score=result["original_score"],
            new_score=result.get("new_score"),
            trace_id=trace_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model/info")
async def get_model_info(
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retorna informações sobre o modelo atual
    """
    try:
        return model_manager.get_model_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 