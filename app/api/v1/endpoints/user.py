from fastapi import APIRouter, Depends, status
from typing import List
from app.auth.jwt import create_access_token, create_refresh_token, decode_refresh_token
from app.service.user import UserService
from app.schemas.user import *
from app.core.exceptions import AppError
from app.api.deps import get_user_service
from app.auth.deps import get_current_user, allow_admin

router = APIRouter(prefix="/v1/auth", tags=["Auth"])

@router.get("/", response_model=List[UserOut], status_code=status.HTTP_200_OK)
def get_all_users(
    service: UserService = Depends(get_user_service),
    admin_user = Depends(allow_admin)
):
    return service.get_all()

@router.get("/username/{username}", response_model=UserOut, status_code=status.HTTP_200_OK)
def get_user_by_username(
    username: str, 
    service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_user)
):
    user = service.get_by_username(username=username.strip())
    if not user:
        raise AppError(404, "USER_NOT_FOUND", "El usuario no existe")
        
    # Validar privacidad: Solo el propio usuario o admin puede ver los detalles
    if current_user.role != "admin" and current_user.username != user.username:
        raise AppError(403, "FORBIDDEN", "No tienes permiso para ver esta información")
        
    return user

@router.get("/email/{email}", response_model=UserOut, status_code=status.HTTP_200_OK)
def get_user_by_email(
    email: str, 
    service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_user)
):
    user = service.get_by_email(email=email.strip())
    if not user:
        raise AppError(404, "USER_NOT_FOUND", "El usuario no existe")
        
    # Validar privacidad: Solo el propio usuario o admin puede ver los detalles
    if current_user.role != "admin" and current_user.user_id != user.id:
        raise AppError(403, "FORBIDDEN", "No tienes permiso para ver esta información")
        
    return user

@router.get("/id/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def get_user_by_id(
    user_id: int, 
    service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_user)
):
    user = service.get_by_id(user_id=user_id)
    if not user:
        raise AppError(404, "USER_NOT_FOUND", "El usuario no existe")
        
    # Validar privacidad: Solo el propio usuario o admin puede ver los detalles
    if current_user.role != "admin" and current_user.user_id != user.id:
        raise AppError(403, "FORBIDDEN", "No tienes permiso para ver esta información")
        
    return user

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, service: UserService = Depends(get_user_service)):
    '''
    Registra un nuevo usuario.
    
    Validaciones automáticas en UserService:
    - Email y username únicos
    - Contraseña hasheada con bcrypt
    - SIEMPRE se crea con role "user" por seguridad
    '''
    return service.create(
        email=payload.email, 
        username=payload.username, 
        password=payload.password,
        role="user"  # SIEMPRE crear como user, ignorar el role del payload
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
    
    # Crear tokens JWT
    token_data = {
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)
    
    # Retornar token y datos del usuario
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/refresh", response_model=Token, status_code=status.HTTP_200_OK)
def refresh_token_endpoint(payload: TokenRefresh, service: UserService = Depends(get_user_service)):
    '''
    Renueva el Access Token usando un Refresh Token válido.
    Permite obtener un nuevo token de acceso sin que el usuario tenga que loguearse de nuevo.
    '''
    # 1. Validar el refresh token
    token_data = decode_refresh_token(payload.refresh_token)
    if not token_data:
         raise AppError(401, "INVALID_TOKEN", "Refresh token inválido, expirado o de tipo incorrecto")
    
    # 2. Verificar que el usuario aún existe en la BD (query ligera)
    # Esto invalida tokens de usuarios eliminados
    user_id = token_data.get("user_id")
    user = service.get_by_id_light(user_id=user_id)
    if not user:
        raise AppError(401, "USER_NOT_FOUND", "El usuario asociado al token no existe")
        
    # 3. Generar nuevos tokens
    new_token_data = {
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }
    
    new_access_token = create_access_token(data=new_token_data)
    new_refresh_token = create_refresh_token(data=new_token_data)
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "user": user
    }

@router.patch("/{user_id}/change-role", response_model=UserOut, status_code=status.HTTP_200_OK)
def change_user_role(
    user_id: int,
    payload: RoleUpdate,
    service: UserService = Depends(get_user_service),
    admin_user = Depends(allow_admin)
):
    '''
    Cambia el role de un usuario. Solo accesible para admins.
    
    Permite promocionar usuarios a admin o degradar admins a user.
    '''
    return service.update(user_id=user_id, user_data={"role": payload.role})

@router.put("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def update_user(
    user_id: int, 
    payload: UserUpdate, 
    service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_user)
):
    # Validar que el usuario solo pueda editarse a sí mismo (salvo que sea admin)
    if current_user.role != "admin" and current_user.user_id != user_id:
        raise AppError(403, "FORBIDDEN", "No tienes permiso para editar este usuario")
    
    # Asegurar que no se puede cambiar el role desde aquí
    update_data = payload.model_dump(exclude_unset=True)
    if "role" in update_data:
        del update_data["role"]  # Eliminar role si viene en el payload
        
    return service.update(user_id=user_id, user_data=update_data)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int, 
    service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_user)
):
    # Validar que el usuario solo pueda borrarse a sí mismo (salvo que sea admin)
    if current_user.role != "admin" and current_user.user_id != user_id:
        raise AppError(403, "FORBIDDEN", "No tienes permiso para eliminar este usuario")

    service.delete(user_id=user_id)
