from pydantic import BaseModel

class CountryBase(BaseModel):
    name: str

class CountryCreate(CountryBase):
    pass

class CountryRead(CountryBase):
    pass

class CountryUpdate(CountryBase):
    pass

class CountryDelete(BaseModel):
    pass