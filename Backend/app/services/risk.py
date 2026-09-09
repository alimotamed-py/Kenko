"""
An important point

These ranges are not medical criteria for risk assessment; they are merely categories for displaying the model's output.
"""

def get_risk_level(probability: float) -> str:
    if probability < 20:
        return "low"

    if probability < 50:
        return "moderate"

    if probability < 80:
        return "high"

    return "very_high"