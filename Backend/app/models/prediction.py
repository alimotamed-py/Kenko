from datetime import datetime, timezone
from sqlmodel import Field, SQLModel


class PredictionHistory(SQLModel, table=True):
    __tablename__ = "prediction_history"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    prediction: int
    probability: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))