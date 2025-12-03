from pydantic import BaseModel, ConfigDict
from datetime import datetime

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    user_id: int
    trip_id: int

class CommentUpdate(CommentBase):
    pass

class CommentDelete(BaseModel):
    pass

class CommentOut(CommentBase):
    id: int
    user_id: int
    trip_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)