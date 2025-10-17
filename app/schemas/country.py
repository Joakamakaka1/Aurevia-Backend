from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CountryBase(BaseModel):
    name: str
    iso_code: str

    class Config:
        orm_mode = True

class CountryCreate(CountryBase):
    continent: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class CountryUpdate(CountryBase):
    pass

class CountryDelete(BaseModel):
    pass