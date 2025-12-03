from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional

# ============================================================================
# SCHEMAS BÁSICOS (sin relaciones) - Para usar dentro de otros schemas
# ============================================================================

class CommentBasic(BaseModel):
    """Schema básico de comentario para usar en relaciones"""
    id: int
    user_id: int
    content: str
    
    model_config = ConfigDict(from_attributes=True)

# ============================================================================
# SCHEMAS DE ENTRADA (Create/Update)
# ============================================================================

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    user_id: int
    trip_id: int
    
    @field_validator('content')
    @classmethod
    def validate_content_length(cls, v: str) -> str:
        if len(v) < 5:
            raise ValueError('El comentario debe tener al menos 5 caracteres')
        if len(v) > 200:
            raise ValueError('El comentario no puede tener más de 200 caracteres')
        return v

class CommentUpdate(BaseModel):
    content: Optional[str] = None
    
    @field_validator('content')
    @classmethod
    def validate_content_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v) < 5:
                raise ValueError('El comentario debe tener al menos 5 caracteres')
            if len(v) > 200:
                raise ValueError('El comentario no puede tener más de 200 caracteres')
        return v

# ============================================================================
# SCHEMA DE SALIDA (Out) - Para respuestas principales
# ============================================================================

class CommentOut(BaseModel):
    """Schema completo de comentario para respuestas"""
    id: int
    user_id: int
    trip_id: int
    content: str
    
    model_config = ConfigDict(from_attributes=True)