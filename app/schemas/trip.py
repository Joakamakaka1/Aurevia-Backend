from pydantic import BaseModel, ConfigDict

# Solo datos del viaje
class TripBase(BaseModel):
    # Estos son los datos fundamentales del viaje
    name: str
    description: str
    start_date: str
    end_date: str

# Añade la FK: user_id
class TripCreate(TripBase):
    # Hereda los campos de TripBase. Solo se añade el user_id.
    user_id: int 

# Solo datos del viaje
class TripUpdate(TripBase):
    pass

# Vacío, solo se usa en el endpoint si aplica
class TripDelete(BaseModel):
    pass

# Define el orden de salida
class TripOut(BaseModel):
    id: int
    user_id: int
    name: str
    description: str
    start_date: str
    end_date: str
    
    model_config = ConfigDict(from_attributes=True)