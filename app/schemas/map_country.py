from pydantic import BaseModel, ConfigDict
from datetime import datetime
from country import CountryBase

class MapCountryBase(BaseModel):
    map_id: int
    country_id: int

class MapCountryCreate(MapCountryBase):
    pass

class MapCountryRead(MapCountryBase):
    id: int
    first_visited: datetime
    visit_count: int                                                                                                                                                                                                                                                                       
    last_visit: datetime
    
    model_config = ConfigDict(from_attributes=True)

class MapCountryWithCountry(MapCountryRead):
    """Schema con información del país incluida"""
    country: 'CountryBase'
    
    model_config = ConfigDict(from_attributes=True)