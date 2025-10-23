from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TripBase(BaseModel):
    title: str
    description: Optional[str] = None
    # photo: Optional[str] = None

    class Config:
        orm_mode = True

class TripCreate(TripBase):
    start_date: datetime
    end_date: datetime
    user_id: int

class TripUpdate(TripBase):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class TripDelete(BaseModel):
    pass

    