from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    nombre: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    nombre: str | None = None
    
    class Config:
        from_attributes = True
