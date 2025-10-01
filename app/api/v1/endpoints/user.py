from fastapi import APIRouter
from typing import List
from app.schemas.user import UserOut

router = APIRouter()

@router.get("/", response_model=List[UserOut])
def get_users():
    return [{"id": 1, "email": "ejemplo@email.com", "nombre": "Juan"}]
