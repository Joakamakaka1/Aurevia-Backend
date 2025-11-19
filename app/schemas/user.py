from pydantic import BaseModel, EmailStr, ConfigDict
from app.schemas.trip import TripOut

# Datos usuario
class UserBase(BaseModel):
    id: int
    email: EmailStr
    username: str

# Datos del usuario al crear una cuenta
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    hashed_password: str

# Datos del usuario al iniciar sesion
class UserLogin(BaseModel):
    email: EmailStr
    hashed_password: str

# Datos del usuario al actualizar
class UserUpdate(UserBase):
    hashed_password: str
    
    pass

# Vacío, solo se usa en el endpoint si aplica
class TripDelete(BaseModel):
    pass

# Datos del usuario al obtenerlo
class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str 
    trips: list[TripOut] = []
    
    model_config = ConfigDict(from_attributes=True)
