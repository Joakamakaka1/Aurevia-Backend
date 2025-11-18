from pydantic import BaseModel, EmailStr, ConfigDict

class TripBase(BaseModel):
    name: str
    description: str
    start_date: str
    end_date: str

    user_id: int

class TripCreate(TripBase):
    pass

class TripUpdate(TripBase):
    pass

class TripDelete(BaseModel):
    pass