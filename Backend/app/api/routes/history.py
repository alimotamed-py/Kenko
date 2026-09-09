from math import ceil
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, func
from app.core.database import get_session
from app.dependencies import get_current_user, verify_csrf
from app.models.prediction import PredictionHistory
from app.models.user import User
from app.schemas.history import (
    PredictionHistoryListResponse,
    PredictionHistoryResponse,
)



router = APIRouter(prefix="/history", tags=["Prediction History"])


@router.get("", response_model=PredictionHistoryListResponse)
def get_prediction_history(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    count_statement = (
        select(func.count())
        .select_from(PredictionHistory)
        .where(PredictionHistory.user_id == current_user.id)
    )

    total = session.exec(count_statement).one()

    pages = ceil(total / limit) if total > 0 else 0

    statement = (
        select(PredictionHistory)
        .where(PredictionHistory.user_id == current_user.id)
        .order_by(PredictionHistory.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )

    items = session.exec(statement).all()

    return PredictionHistoryListResponse(items=items, total=total, page=page, limit=limit, pages=pages)


@router.get("/{history_id}", response_model=PredictionHistoryResponse)
def get_prediction_history_detail(history_id: int, current_user: User = Depends(get_current_user),
                                  session: Session = Depends(get_session)):
    statement = select(PredictionHistory).where(PredictionHistory.id == history_id,
                                                PredictionHistory.user_id == current_user.id,)

    history = session.exec(statement).first()

    if history is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction history not found.",)
    return history


@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_csrf)])
def delete_prediction_history(history_id: int, current_user: User = Depends(get_current_user),
                              session: Session = Depends(get_session)):
    statement = select(PredictionHistory).where(PredictionHistory.id == history_id,
                                                PredictionHistory.user_id == current_user.id)

    history = session.exec(statement).first()

    if history is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction history not found.")
    session.delete(history)
    session.commit()