from typing import Literal
from pydantic import BaseModel, Field


class HeartDiseaseInput(BaseModel):
    age: int = Field(..., ge=18, le=120)

    sex: Literal["Male", "Female"]

    resting_bp_systolic: float = Field(..., gt=0)
    resting_bp_diastolic: float = Field(..., gt=0)

    cholesterol_total: float = Field(..., gt=0)
    hdl: float = Field(..., gt=0)
    ldl: float = Field(..., gt=0)
    triglycerides: float = Field(..., gt=0)

    fasting_blood_sugar: float = Field(..., ge=0)
    hba1c: float = Field(..., ge=0)

    bmi: float = Field(..., gt=0)

    resting_heart_rate: int = Field(..., gt=0)
    max_heart_rate_achieved: int = Field(..., gt=0)

    chest_pain_type: Literal["Asymptomatic", "Non-Anginal Pain", "Atypical Angina", "Typical Angina"]

    exercise_induced_angina: bool

    st_depression: float = Field(..., ge=0)

    family_history: bool

    smoker_status: Literal["Never", "Former", "Current"]

    alcohol_units_per_week: float = Field(..., ge=0)

    exercise_minutes_per_week: int = Field(..., ge=0)

    sleep_hours: float = Field(..., ge=0)

    stress_score: float = Field(..., ge=0, le=100)

    wearable_owner: bool

    daily_steps: int = Field(..., ge=0)

    diet_quality_score: float = Field(..., ge=0, le=100)


class HeartDiseasePrediction(BaseModel):
    prediction: Literal[0, 1]
    result: Literal["Heart Disease", "No Heart Disease"]

    probability: float = Field(..., ge=0, le=100)

    risk_level: Literal["low", "moderate", "high", "very_high"]

    recommendations: list[str]

    message: str


class PredictionResponse(BaseModel):
    success: bool
    data: HeartDiseasePrediction


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list | None = None


class ErrorResponse(BaseModel):
    success: Literal[False]
    error: ErrorDetail