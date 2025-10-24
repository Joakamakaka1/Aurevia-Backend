from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    hashed_password: str

class UserLogin(BaseModel):
    email: EmailStr
    hashed_password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str | None = None
    hashed_password: str | None = None
    
    model_config = ConfigDict(from_attributes=True)
