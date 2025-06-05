from fastapi import APIRouter
from ....schemas.score import ScoreRequest, ScoreResponse
from ....services.score_service import ScoreService

router = APIRouter()
service = ScoreService()

@router.get("/healthz", summary="Health check")
def health_check():
    return {"status": "ok"}

@router.post("/predict", response_model=ScoreResponse, summary="Predict score")
def predict_score(payload: ScoreRequest):
    score = service.predict_score(payload.features)
    return ScoreResponse(score=score)
