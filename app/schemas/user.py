from pydantic import BaseModel, EmailStr

class UserOut(BaseModel):
    id: int
    email: EmailStr
    nombre: str

    class Config:
        from_attributes = True
