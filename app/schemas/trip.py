from datetime import date
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from app.schemas.country import CountryBasic
from app.schemas.comment import CommentBasic

# ============================================================================
# SCHEMAS BÁSICOS (sin relaciones) - Para usar dentro de otros schemas
# ============================================================================

class TripBasic(BaseModel):
    """Schema básico de viaje para usar en relaciones (ej: dentro de UserOut)"""
    id: int
    name: str
    description: str
    start_date: date
    end_date: date
    country: CountryBasic  # Solo info básica del país
    
    model_config = ConfigDict(from_attributes=True)

# ============================================================================
# SCHEMAS DE ENTRADA (Create/Update)
# ============================================================================

class TripBase(BaseModel):
    name: str
    description: str
    start_date: date
    end_date: date

class TripCreate(TripBase):
    user_id: int 
    country_id: int
    
    @field_validator('name')
    @classmethod
    def validate_name_length(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError('El nombre del viaje debe tener al menos 3 caracteres')
        if len(v) > 100:
            raise ValueError('El nombre del viaje no puede tener más de 100 caracteres')
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description_length(cls, v: str) -> str:
        if len(v) < 10:
            raise ValueError('La descripción debe tener al menos 10 caracteres')
        if len(v) > 500:
            raise ValueError('La descripción no puede tener más de 500 caracteres')
        return v

class TripUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    country_id: Optional[int] = None
    
    @field_validator('name')
    @classmethod
    def validate_name_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v) < 3:
                raise ValueError('El nombre del viaje debe tener al menos 3 caracteres')
            if len(v) > 100:
                raise ValueError('El nombre del viaje no puede tener más de 100 caracteres')
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v) < 10:
                raise ValueError('La descripción debe tener al menos 10 caracteres')
            if len(v) > 500:
                raise ValueError('La descripción no puede tener más de 500 caracteres')
        return v

    @field_validator('start_date', 'end_date')
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        try:
            # Validar formato YYYY-MM-DD
            date.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError('La fecha debe estar en formato YYYY-MM-DD')

# ============================================================================
# SCHEMA DE SALIDA (Out) - Para respuestas principales
# ============================================================================

class TripOut(BaseModel):
    """Schema completo de viaje con relaciones para respuestas"""
    id: int
    user_id: int
    name: str
    description: str
    start_date: date
    end_date: date
    country: CountryBasic  # Info básica del país
    comments: list[CommentBasic] = []  # Lista de comentarios (básicos, sin anidación profunda)
    
    model_config = ConfigDict(from_attributes=True)