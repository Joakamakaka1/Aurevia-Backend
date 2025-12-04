from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.orm import Session
from app.auth.deps import get_db
from app.auth.jwt import create_access_token
from app.service import user as crud_user
from app.schemas.user import *
from app.core.exceptions import AppError

router = APIRouter(prefix="/v1/auth", tags=["Auth"])

@router.get("/", response_model=List[UserOut], status_code=status.HTTP_200_OK)
def get_all_users(db: Session = Depends(get_db)):
    return crud_user.get_all_users(db)

@router.get("/username/{username}", response_model=UserOut, status_code=status.HTTP_200_OK)
def get_user_by_username(username: str, db: Session = Depends(get_db)):
    user = crud_user.get_by_username(db, username=username.strip())
    if not user:
        raise AppError(404, "USER_NOT_FOUND", "El usuario no existe")
    return user

@router.get("/email/{email}", response_model=UserOut, status_code=status.HTTP_200_OK)
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    user = crud_user.get_by_email(db, email=email.strip())
    if not user:
        raise AppError(404, "USER_NOT_FOUND", "El usuario no existe")
    return user

@router.get("/id/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = crud_user.get_user_by_id(db, user_id=user_id)
    if not user:
        raise AppError(404, "USER_NOT_FOUND", "El usuario no existe")
    return user

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    return crud_user.create(
        db, 
        email=payload.email, 
        username=payload.username, 
        password=payload.password,
        role=payload.role
    )

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    # Autenticar usuario
    user = crud_user.authenticate(db, email=payload.email, password=payload.password)
    
    # Crear token JWT con información del usuario
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "username": user.username,
            "role": user.role
        }
    )
    
    # Retornar token y datos del usuario
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.put("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    return crud_user.update_user_by_id(db, user_id=user_id, user_data=payload.model_dump(exclude_unset=True))

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    crud_user.delete_user_by_id(db, user_id=user_id)


