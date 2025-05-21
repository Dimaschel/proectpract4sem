from fastapi import APIRouter, Depends, Query, Path, HTTPException
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

@router.post("/", response_model=schemas.CategoryOut)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db), owner_id: int = Query(1, description="ID владельца")):
    db_category = models.Category(**category.dict(), owner_id=owner_id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/", response_model=List[schemas.CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()

@router.delete("/{category_id}", summary="Удаление категории без транзакций", tags=["Categories"])
def delete_category_if_empty(
    category_id: int = Path(..., description="ID категории"),
    owner_id: int = Query(1, description="ID владельца"),
    db: Session = Depends(get_db)
):
    category = db.query(models.Category).filter_by(id=category_id, owner_id=owner_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена или не принадлежит владельцу")

    if category.transactions:
        raise HTTPException(status_code=400, detail="Невозможно удалить категорию,в ней есть транзакции")

    db.delete(category)
    db.commit()

    return {"message": f"Категория с ID {category_id} успешно удалена"}
