from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import SessionLocal
from app.models import Transaction, TransactionType

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/statistics/by_owner", summary="Статистика по доходам и расходам владельца", tags=["User_Statistics"])
def statistics_by_owner(
    owner_id: int = Query(..., description="ID владельца"),
    db: Session = Depends(get_db)
):
    income_total = db.query(func.coalesce(func.sum(Transaction.amount), 0.0))\
        .filter(
            Transaction.owner_id == owner_id,
            Transaction.type == TransactionType.INCOME
        ).scalar()

    expense_total = db.query(func.coalesce(func.sum(Transaction.amount), 0.0))\
        .filter(
            Transaction.owner_id == owner_id,
            Transaction.type == TransactionType.EXPENSE
        ).scalar()

    return {
        "owner_id": owner_id,
        "income": income_total,
        "expense": expense_total
    }