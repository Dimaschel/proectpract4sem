from fastapi import FastAPI
from app.routes import transaction_routes, category_routes, budget_routes, user_routes, ownerstat_routes
from app import models
from app.database import engine

app = FastAPI()

app.include_router(category_routes.router, prefix="/categories", tags=["Categories"])
app.include_router(transaction_routes.router, prefix="/transactions", tags=["Transactions"])
app.include_router(budget_routes.router, prefix="/budgets", tags=["Budgets"])
app.include_router(user_routes.router, prefix="/users", tags=["Users"])
app.include_router(ownerstat_routes.router, prefix="/User_Statistics", tags=["User_Statistics"] )
models.Base.metadata.create_all(bind=engine)