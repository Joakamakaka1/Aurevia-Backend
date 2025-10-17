from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.orm import Session
from app.auth.deps import get_db
from app.service import user as crud_user
from app.schemas.user import UserCreate, UserLogin, UserOut

router = APIRouter(prefix="/v1/auth", tags=["Auth"])

@router.get("/", response_model=List[UserOut])
def get_users():
    return [{"id": 1, "email": "ejemplo@email.com", "username": "Juan"}]

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    return crud_user.create(db, email=payload.email, username=payload.username, password=payload.password)

@router.post("/login", response_model=UserOut, status_code=status.HTTP_200_OK)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = crud_user.authenticate(db, email=payload.email, password=payload.password)
    return user
