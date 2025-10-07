from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from app.auth.deps import get_db, get_current_user_basic
from app.crud import user as crud_user
from app.schemas.user import UserCreate, UserLogin, UserOut

router = APIRouter(prefix="/v1/auth", tags=["Auth"])

@router.get("/", response_model=List[UserOut])
def get_users():
    return [{"id": 1, "email": "ejemplo@email.com", "nombre": "Juan"}]

@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if crud_user.get_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email ya registrado")
    return crud_user.create(db, email=payload.email, nombre=payload.nombre, password=payload.password)

@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = crud_user.authenticate(db, email=payload.email, password=payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Credenciales inválidas")
    return {"message": "OK"}  # El cliente guardará email+password y usará Basic en cada llamada.
