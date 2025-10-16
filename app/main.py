from fastapi import FastAPI
from app.api.v1 import api_router
from app.db.session import engine
from app.db.base import Base
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import (
    AppError, app_error_handler, validation_error_handler, unhandled_error_handler
)
app = FastAPI(title="Aurevia API")
Base.metadata.create_all(bind=engine)
app.include_router(api_router, prefix="/api")

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)

origins = [
    "http://localhost:8100",   # Tu frontend en Ionic o similar
    "http://127.0.0.1:8100",  # Otra posible variación
    "http://localhost:4200",       # Permitir localhost sin puerto
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Puedes usar ["*"] para permitir todos (no recomendado en prod)
    allow_credentials=True,
    allow_methods=["*"],     # Métodos permitidos: GET, POST, etc.
    allow_headers=["*"],     # Headers permitidos
)
