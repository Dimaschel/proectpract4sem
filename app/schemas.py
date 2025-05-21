from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum
from app import models

class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    RUB = "RUB"

class UserCreate(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    default_currency: Currency

    class Config:
        orm_mode = True

class CategoryCreate(BaseModel):
    name: str
    type: TransactionType

class CategoryOut(CategoryCreate):
    id: int

    class Config:
        orm_mode = True

class TransactionCreate(BaseModel):
    amount: float
    description: Optional[str] = None
    category_id: int
    currency: Currency = Currency.RUB
    type: TransactionType

class TransactionOut(TransactionCreate):
    id: int
    date: datetime

    class Config:
        orm_mode = True

class BudgetCreate(BaseModel):
    amount: float
    start_date: datetime
    end_date: datetime
    category_id: int

class BudgetOut(BudgetCreate):
    id: int

    class Config:
        orm_mode = True
