from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional

# ============================================================================
# SCHEMAS BÁSICOS (sin relaciones) - Para usar dentro de otros schemas
# ============================================================================

class CountryBasic(BaseModel):
    """Schema básico de país para usar en relaciones"""
    id: int
    name: str
    code_alpha2: Optional[str] = None
    code_alpha3: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# ============================================================================
# SCHEMAS DE ENTRADA (Create/Update)
# ============================================================================

class CountryBase(BaseModel):
   name: str

class CountryCreate(CountryBase):
    code_alpha2: Optional[str] = None
    code_alpha3: Optional[str] = None
    capital: Optional[str] = None
    region: Optional[str] = None
    subregion: Optional[str] = None
    population: Optional[int] = None
    flag_url: Optional[str] = None
    
    @field_validator('name')
    @classmethod
    def validate_name_length(cls, v: str) -> str:
        if len(v) < 2:
            raise ValueError('El nombre del país debe tener al menos 2 caracteres')
        if len(v) > 100:
            raise ValueError('El nombre del país no puede tener más de 100 caracteres')
        return v
    
    @field_validator('code_alpha2')
    @classmethod
    def validate_alpha2(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) != 2:
            raise ValueError('El código alpha-2 debe tener exactamente 2 caracteres')
        return v.upper() if v else None
    
    @field_validator('code_alpha3')
    @classmethod
    def validate_alpha3(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) != 3:
            raise ValueError('El código alpha-3 debe tener exactamente 3 caracteres')
        return v.upper() if v else None

class CountryUpdate(BaseModel):
    name: Optional[str] = None
    code_alpha2: Optional[str] = None
    code_alpha3: Optional[str] = None
    capital: Optional[str] = None
    region: Optional[str] = None
    subregion: Optional[str] = None
    population: Optional[int] = None
    flag_url: Optional[str] = None
    
    @field_validator('name')
    @classmethod
    def validate_name_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v) < 2:
                raise ValueError('El nombre del país debe tener al menos 2 caracteres')
            if len(v) > 100:
                raise ValueError('El nombre del país no puede tener más de 100 caracteres')
        return v
    
    @field_validator('code_alpha2')
    @classmethod
    def validate_alpha2(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) != 2:
            raise ValueError('El código alpha-2 debe tener exactamente 2 caracteres')
        return v.upper() if v else None
    
    @field_validator('code_alpha3')
    @classmethod
    def validate_alpha3(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) != 3:
            raise ValueError('El código alpha-3 debe tener exactamente 3 caracteres')
        return v.upper() if v else None

# ============================================================================
# SCHEMA DE SALIDA (Out) - Para respuestas principales
# ============================================================================

class CountryOut(BaseModel):
    """Schema completo de país para respuestas (sin cities para evitar anidación excesiva)"""
    id: int
    name: str
    code_alpha2: Optional[str] = None
    code_alpha3: Optional[str] = None
    capital: Optional[str] = None
    region: Optional[str] = None
    subregion: Optional[str] = None
    population: Optional[int] = None
    flag_url: Optional[str] = None
    # NO incluimos cities aquí para evitar problemas circulares y anidación excesiva
    # Si necesitas las ciudades de un país, usa el endpoint: /city/ y filtra por country_id

    model_config = ConfigDict(from_attributes=True)
