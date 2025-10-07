from fastapi import FastAPI
from app.api.v1 import api_router
from app.db.session import engine
from app.db.base import Base

app = FastAPI(title="Aurevia API")
Base.metadata.create_all(bind=engine)
app.include_router(api_router, prefix="/api")

