from pydantic import BaseModel, ConfigDict

class CountryBase(BaseModel):
   id: int
   name: str

class CountryCreate(CountryBase):
    pass

class CountryUpdate(CountryBase):
    pass

class CountryDelete(BaseModel):
    pass

class CountryOut(CountryBase):
    pass

    model_config = ConfigDict(from_attributes=True)