from fastapi import APIRouter, Depends, status
from typing import List
from app.auth.jwt import create_access_token
from app.service.user import UserService
from app.schemas.user import *
from app.core.exceptions import AppError
from app.api.deps import get_user_service

router = APIRouter(prefix="/v1/auth", tags=["Auth"])

@router.get("/", response_model=List[UserOut], status_code=status.HTTP_200_OK)
def get_all_users(service: UserService = Depends(get_user_service)):
    return service.get_all()

@router.get("/username/{username}", response_model=UserOut, status_code=status.HTTP_200_OK)
def get_user_by_username(username: str, service: UserService = Depends(get_user_service)):
    user = service.get_by_username(username=username.strip())
    if not user:
        raise AppError(404, "USER_NOT_FOUND", "El usuario no existe")
    return user

@router.get("/email/{email}", response_model=UserOut, status_code=status.HTTP_200_OK)
def get_user_by_email(email: str, service: UserService = Depends(get_user_service)):
    user = service.get_by_email(email=email.strip())
    if not user:
        raise AppError(404, "USER_NOT_FOUND", "El usuario no existe")
    return user

@router.get("/id/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def get_user_by_id(user_id: int, service: UserService = Depends(get_user_service)):
    user = service.get_by_id(user_id=user_id)
    if not user:
        raise AppError(404, "USER_NOT_FOUND", "El usuario no existe")
    return user

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, service: UserService = Depends(get_user_service)):
    '''
    Registra un nuevo usuario.
    
    Validaciones automáticas en UserService:
    - Email y username únicos
    - Contraseña hasheada con bcrypt
    '''
    return service.create(
        email=payload.email, 
        username=payload.username, 
        password=payload.password,
        role=payload.role
    )

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(payload: UserLogin, service: UserService = Depends(get_user_service)):
    '''
    Autentica un usuario y genera un token JWT.
    
    Proceso:
    1. Verifica email y contraseña
    2. Genera token JWT con datos del usuario (user_id, username, role)
    3. Retorna el token y datos del usuario
    '''
    # Autenticar usuario
    user = service.authenticate(email=payload.email, password=payload.password)
    
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
def update_user(user_id: int, payload: UserUpdate, service: UserService = Depends(get_user_service)):
    return service.update(user_id=user_id, user_data=payload.model_dump(exclude_unset=True))

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, service: UserService = Depends(get_user_service)):
    service.delete(user_id=user_id)
