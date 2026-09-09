import joblib
import pandas as pd
from app.core.config import settings
from app.services.recommendations import get_recommendations
from app.core.exceptions import KenkoError
from app.core.logging import logger
from app.schemas.heart_disease import HeartDiseaseInput
from app.services.encoding import (
    SEX_MAPPING,
    FAMILY_HISTORY_MAPPING,
    CHEST_PAIN_MAPPING,
    EXERCISE_ANGINA_MAPPING,
    SMOKER_STATUS_MAPPING,
    WEARABLE_OWNER_MAPPING,
)
from app.services.risk import get_risk_level



FEATURE_ORDER = [
    "age",
    "sex",
    "resting_bp_systolic",
    "resting_bp_diastolic",
    "cholesterol_total",
    "hdl",
    "ldl",
    "triglycerides",
    "fasting_blood_sugar",
    "hba1c",
    "bmi",
    "resting_heart_rate",
    "max_heart_rate_achieved",
    "chest_pain_type",
    "exercise_induced_angina",
    "st_depression",
    "family_history",
    "smoker_status",
    "alcohol_units_per_week",
    "exercise_minutes_per_week",
    "sleep_hours",
    "stress_score",
    "wearable_owner",
    "daily_steps",
    "diet_quality_score",
]


class HeartDiseasePredictor:
    def __init__(self):
        model_data = joblib.load(settings.model_path)

        self.model = model_data["model"]
        self.scaler = model_data["scaler"]

    def predict(self, data: HeartDiseaseInput):
        logger.info("Heart disease prediction started.")

        try:
            input_data = data.model_dump()

            # Encode categorical features
            input_data["sex"] = SEX_MAPPING[input_data["sex"]]

            input_data["family_history"] = FAMILY_HISTORY_MAPPING[input_data["family_history"]]

            input_data["chest_pain_type"] = CHEST_PAIN_MAPPING[input_data["chest_pain_type"]]

            input_data["exercise_induced_angina"] = EXERCISE_ANGINA_MAPPING[input_data["exercise_induced_angina"]]

            input_data["smoker_status"] = SMOKER_STATUS_MAPPING[input_data["smoker_status"]]

            input_data["wearable_owner"] = WEARABLE_OWNER_MAPPING[input_data["wearable_owner"]]

            # Keep exactly the same feature order used during training
            df = pd.DataFrame([[input_data[feature] for feature in FEATURE_ORDER]], columns=FEATURE_ORDER)

            # Scale features
            scaled_data = self.scaler.transform(df)

            # Prediction
            prediction = int(self.model.predict(scaled_data)[0])

            logger.info("Heart disease prediction completed: prediction=%s", prediction)

            # Probability of class 1
            probability = float(self.model.predict_proba(scaled_data)[0][1])
            probability_percent = round(probability * 100, 2)
            risk_level = get_risk_level(probability_percent)
            recommendations = get_recommendations(data)

            if prediction == 1:
                result = "Heart Disease"
                message = (
                    "I am an artificial intelligence model, not a doctor. "
                    "This result indicates a possible risk of heart disease. "
                    "Please consult a qualified physician for proper evaluation."
                )
            else:
                result = "No Heart Disease"
                message = (
                    "I am an artificial intelligence model, not a doctor. "
                    "This result does not indicate heart disease based on the "
                    "provided information. If you have symptoms or concerns, "
                    "please consult a qualified physician."
                )

            return {
                "success": True,
                "data": {
                    "prediction": prediction,
                    "result": result,
                    "probability": probability_percent,
                    "risk_level": risk_level,
                    "recommendations": recommendations,
                    "message": message,
                },
            }

        except Exception:
            logger.exception("Heart disease prediction failed.")

            raise KenkoError(status_code=500, code="PREDICTION_ERROR", message="Unable to process the prediction.",
                             details=None)

heart_disease_predictor = HeartDiseasePredictor()