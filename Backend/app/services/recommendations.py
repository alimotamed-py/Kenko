from app.schemas.heart_disease import HeartDiseaseInput


def get_recommendations(data: HeartDiseaseInput) -> list[str]:
    recommendations: list[str] = []

    # Blood pressure
    if data.resting_bp_systolic >= 140 or data.resting_bp_diastolic >= 90:
        recommendations.append(
            "Monitor your blood pressure regularly and discuss elevated readings with a healthcare professional."
        )

    # Cholesterol
    if data.ldl >= 130 or data.cholesterol_total >= 200:
        recommendations.append(
            "Consider discussing your cholesterol and LDL levels with a healthcare professional."
        )

    # Physical activity
    if data.exercise_minutes_per_week < 150:
        recommendations.append(
            "Consider increasing regular physical activity according to your individual health condition."
        )

    # Sleep
    if data.sleep_hours < 7:
        recommendations.append(
            "Try to maintain a regular sleep schedule and aim for sufficient sleep."
        )

    # Stress
    if data.stress_score >= 70:
        recommendations.append(
            "Consider healthy stress-management strategies such as regular activity, relaxation, or professional support."
        )

    # Smoking
    if data.smoker_status == "Current":
        recommendations.append(
            "Consider quitting smoking and seek professional support if needed."
        )

    # BMI
    if data.bmi >= 30:
        recommendations.append(
            "Consider discussing healthy weight-management strategies with a healthcare professional."
        )

    # Alcohol
    if data.alcohol_units_per_week > 7:
        recommendations.append(
            "Consider reducing alcohol consumption and discussing your alcohol intake with a healthcare professional."
        )

    # General recommendation
    if not recommendations:
        recommendations.append(
            "Maintain a healthy lifestyle with regular physical activity, balanced nutrition, adequate sleep, and routine health checkups."
        )

    return recommendations