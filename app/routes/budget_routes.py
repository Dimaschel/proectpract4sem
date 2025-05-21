from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlalchemy.orm import Session

from app import schemas
from app import models
from app.database import SessionLocal
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.BudgetOut)
def create_budget(budget: schemas.BudgetCreate, db: Session = Depends(get_db), owner_id: int = Query(1, description="ID владельца")):

    category = db.query(models.Category).filter_by(id=budget.category_id, owner_id=owner_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Категория не найдена или не принадлежит указанному владельцу.")
    
    db_budget = models.Budget(**budget.dict(), owner_id=owner_id) 
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

@router.get("/", response_model=List[schemas.BudgetOut])
def list_budgets(db: Session = Depends(get_db)):
    return db.query(models.Budget).all()

@router.delete("/{budget_id}", summary="Удаление бюджета", tags=["Budgets"])
def delete_budget(
    budget_id: int = Path(..., description="ID бюджета для удаления"),
    owner_id: int = Query(1, description="ID владельца"),
    db: Session = Depends(get_db)
):
    db_budget = db.query(models.Budget).filter_by(id=budget_id, owner_id=owner_id).first()
    if not db_budget:
        raise HTTPException(status_code=404, detail="Бюджет не найден или не принадлежит указанному владельцу.")

    db.delete(db_budget)
    db.commit()

    return {"message": f"Бюджет с ID {budget_id} успешно удален"}