from pydantic import BaseModel, ConfigDict

class CountryBase(BaseModel):
   name: str

class CountryCreate(CountryBase):
    pass

class CountryUpdate(CountryBase):
    pass

class CountryDelete(BaseModel):
    pass

class CountryOut(CountryBase):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)