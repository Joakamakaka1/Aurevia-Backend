from fastapi import FastAPI
from app.api.v1.endpoints import user

# Importaciones necesarias para la DB
from app.db.session import engine
from app.db.base import Base
from app.db.models import user as user_model  # Importa tus modelos

app = FastAPI(title="Aurevia API")

# Crear las tablas automáticamente
Base.metadata.create_all(bind=engine)

# Incluir rutas
app.include_router(user.router, prefix="/api/v1/users", tags=["Users"])
