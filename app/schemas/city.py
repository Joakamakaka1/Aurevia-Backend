from pydantic import BaseModel, ConfigDict

class CityBase(BaseModel):
    name: str
    latitude: float
    longitude: float

class CityCreate(CityBase):
    # country_id: int
    pass

class CityUpdate(CityBase):
    pass

class CityDelete(BaseModel):
    pass

class CityOut(BaseModel):
    id: int
    name: str
    # country_id: int
    latitude: float
    longitude: float
   
    model_config = ConfigDict(from_attributes=True)