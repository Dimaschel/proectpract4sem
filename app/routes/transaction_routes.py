from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app import schemas
from app import models
from app.database import SessionLocal
from typing import List
from app.models import Transaction, TransactionType
from sqlalchemy import func
from datetime import datetime
from fastapi import APIRouter, Depends, Query

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.TransactionOut)
def create_transaction(tx: schemas.TransactionCreate, db: Session = Depends(get_db)):

    category = db.query(models.Category).filter(models.Category.id == tx.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    db_tx = models.Transaction(**tx.dict(), owner_id=category.owner_id)
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    return db_tx

@router.get("/", response_model=List[schemas.TransactionOut])
def list_transactions(db: Session = Depends(get_db)):
    return db.query(models.Transaction).all()

@router.get("/statistics", summary="Статистика за период", tags=["Transactions"])
def transaction_statistics(
    start_date: datetime = Query(..., description="Начало периода"),
    end_date: datetime = Query(..., description="Конец периода"),
    owner_id: int = Query(..., description="ID пользователя (owner)"),
    db: Session = Depends(get_db)
):
    income_total = db.query(Transaction)\
        .filter(
            Transaction.owner_id == owner_id,
            Transaction.type == TransactionType.INCOME,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).with_entities(func.coalesce(func.sum(Transaction.amount), 0.0)).scalar()

    expense_total = db.query(Transaction)\
        .filter(
            Transaction.owner_id == owner_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).with_entities(func.coalesce(func.sum(Transaction.amount), 0.0)).scalar()

    return {
        "income": income_total,
        "expense": expense_total
    }

@router.get("/statistics/by_category", summary="Статистика за период в категории", tags=["Transactions"])
def transaction_statistics_by_category(
    start_date: datetime = Query(..., description="Начало периода"),
    end_date: datetime = Query(..., description="Конец периода"),
    category_id: int = Query(..., description="ID категории"),
    owner_id: int = Query(..., description="ID пользователя (owner)"),
    db: Session = Depends(get_db)
):
    base_filters = [
        Transaction.owner_id == owner_id,
        Transaction.category_id == category_id,
        Transaction.date >= start_date,
        Transaction.date <= end_date,
    ]

    income_total = db.query(func.coalesce(func.sum(Transaction.amount), 0.0))\
        .filter(*base_filters, Transaction.type == TransactionType.INCOME)\
        .scalar()

    expense_total = db.query(func.coalesce(func.sum(Transaction.amount), 0.0))\
        .filter(*base_filters, Transaction.type == TransactionType.EXPENSE)\
        .scalar()

    return {
        "category_id": category_id,
        "owner_id": owner_id,
        "income": income_total,
        "expense": expense_total
    }

@router.delete("/{transaction_id}", summary="Удаление транзакции", tags=["Transactions"])
def delete_transaction(
    transaction_id: int = Path(..., description="ID транзакции для удаления"),
    db: Session = Depends(get_db)
):
    transaction = db.query(models.Transaction).filter_by(id=transaction_id).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Транзакция не найдена")

    db.delete(transaction)
    db.commit()

    return {"message": f"Транзакция с ID {transaction_id} успешно удалена"}