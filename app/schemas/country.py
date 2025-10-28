from pydantic import BaseModel
from typing import Optional

class CountryBase(BaseModel):
    name: str
    iso_code: str
    continent: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        orm_mode = True

class CountryCreate(CountryBase):
    name: str
    iso_code: str
    continent: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class CountryUpdate(CountryBase):
    pass

class CountryDelete(BaseModel):
    pass