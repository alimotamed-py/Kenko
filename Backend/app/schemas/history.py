from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PredictionHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    prediction: int
    probability: float
    created_at: datetime


class PredictionHistoryListResponse(BaseModel):
    items: list[PredictionHistoryResponse]
    total: int
    page: int
    limit: int
    pages: int