from pydantic import BaseModel
from typing import List

class ScoreRequest(BaseModel):
    features: List[float]

class ScoreResponse(BaseModel):
    score: float
