from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from typing import Optional
from app.schemas.trip import TripBasic
from app.schemas.comment import CommentBasic

# ============================================================================
# SCHEMAS BÁSICOS (sin relaciones) - Para usar dentro de otros schemas
# ============================================================================

class UserBasic(BaseModel):
    """Schema básico de usuario para usar en relaciones"""
    id: int
    email: EmailStr
    username: str
    
    model_config = ConfigDict(from_attributes=True)

# ============================================================================
# SCHEMAS DE ENTRADA (Create/Update/Login)
# ============================================================================

class UserBase(BaseModel):
    id: int
    email: EmailStr
    username: str

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str  # El cliente envía la contraseña en texto plano, se hashea en el servidor
    
    @field_validator('username')
    @classmethod
    def validate_username_length(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError('El nombre de usuario debe tener al menos 3 caracteres')
        if len(v) > 50:
            raise ValueError('El nombre de usuario no puede tener más de 50 caracteres')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str  # El cliente envía la contraseña en texto plano

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None  # El cliente envía la contraseña en texto plano
    
    @field_validator('username')
    @classmethod
    def validate_username_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v) < 3:
                raise ValueError('El nombre de usuario debe tener al menos 3 caracteres')
            if len(v) > 50:
                raise ValueError('El nombre de usuario no puede tener más de 50 caracteres')
        return v

# ============================================================================
# SCHEMA DE SALIDA (Out) - Para respuestas principales
# ============================================================================

class UserOut(BaseModel):
    """Schema completo de usuario con relaciones para respuestas"""
    id: int
    email: EmailStr
    username: str 
    trips: list[TripBasic] = []  # Solo info básica de viajes (sin comments anidados)
    comments: list[CommentBasic] = []  # Solo info básica de comentarios (sin viajes anidados)
    # NO incluimos comments del usuario para evitar redundancia
    # Hay endpoint específico para los comentarios del usuario: /comment/user/{user_id}
    
    model_config = ConfigDict(from_attributes=True)
