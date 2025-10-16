from fastapi import FastAPI
from app.api.v1 import api_router
from app.db.session import engine
from app.db.base import Base
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Aurevia API")
Base.metadata.create_all(bind=engine)
app.include_router(api_router, prefix="/api")

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
