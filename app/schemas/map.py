from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class MapBase(BaseModel): # Mapa schema base. Muestra los campos comunes.
    countries_visited: int
    percent_world_visited: float
    map_image_url: Optional[str]

class MapRead(BaseModel): # Mapa schema para lectura. Incluye todos los campos del modelo de base de datos.
    user_id: int
    countries_visited: int
    percent_world_visited: float
    map_image_url: Optional[str]
    last_updated: datetime

class MapDeleted(BaseModel): # Mapa schema para eliminación. Indica si el mapa ha sido eliminado.
    deleted: bool
    
    model_config = ConfigDict(from_attributes=True)
