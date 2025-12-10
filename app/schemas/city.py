from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from app.schemas.country import CountryBasic

# ============================================================================
# SCHEMAS BÁSICOS (sin relaciones) - Para usar dentro de otros schemas
# ============================================================================

class CityBasic(BaseModel):
    """Schema básico de ciudad para usar en relaciones"""
    id: int
    name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    population: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

# ============================================================================
# SCHEMAS DE ENTRADA (Create/Update)
# ============================================================================

class CityBase(BaseModel):
    name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class CityCreate(CityBase):
    country_id: int
    population: Optional[int] = None
    geoname_id: Optional[int] = None
    
    @field_validator('name')
    @classmethod
    def validate_name_length(cls, v: str) -> str:
        if len(v) < 2:
            raise ValueError('El nombre de la ciudad debe tener al menos 2 caracteres')
        if len(v) > 100:
            raise ValueError('El nombre de la ciudad no puede tener más de 100 caracteres')
        return v

class CityUpdate(BaseModel):
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    country_id: Optional[int] = None
    population: Optional[int] = None
    geoname_id: Optional[int] = None
    
    @field_validator('name')
    @classmethod
    def validate_name_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v) < 2:
                raise ValueError('El nombre de la ciudad debe tener al menos 2 caracteres')
            if len(v) > 100:
                raise ValueError('El nombre de la ciudad no puede tener más de 100 caracteres')
        return v

# ============================================================================
# SCHEMA DE SALIDA (Out) - Para respuestas principales
# ============================================================================

class CityOut(BaseModel):
    """Schema completo de ciudad con relaciones para respuestas"""
    id: int
    name: str
    country_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    population: Optional[int] = None
    geoname_id: Optional[int] = None
    country: Optional[CountryBasic] = None
   
    model_config = ConfigDict(from_attributes=True)
