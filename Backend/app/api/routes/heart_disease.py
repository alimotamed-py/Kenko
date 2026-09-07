from fastapi import APIRouter, Depends

from app.dependencies import (
    get_current_user,
    verify_csrf,
)

from app.models.user import User
from app.schemas.heart_disease import (
    ErrorResponse,
    HeartDiseaseInput,
    PredictionResponse,
)
from app.services.prediction import heart_disease_predictor


router = APIRouter(
    prefix="/predict",
    tags=["Prediction"],
)


@router.post(
    "/heart-disease",
    response_model=PredictionResponse,
    dependencies=[Depends(verify_csrf)],
    responses={
        422: {
            "model": ErrorResponse,
            "description": "Validation error",
        },
        500: {
            "model": ErrorResponse,
            "description": "Internal server error",
        },
    },
)
def predict_heart_disease(
    data: HeartDiseaseInput,
    current_user: User = Depends(get_current_user),
):
    return heart_disease_predictor.predict(data)