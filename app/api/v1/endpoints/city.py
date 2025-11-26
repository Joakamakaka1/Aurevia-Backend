from fastapi import APIRouter, Depends, Response, status
from typing import List
from sqlalchemy.orm import Session
from app.auth.deps import get_db
from app.service import city as crud_city
from app.schemas.city import *

router = APIRouter(prefix="/v1/city", tags=["City"])

@router.get("/", response_model=List[CityOut], status_code=status.HTTP_200_OK)
def get_all_cities(db: Session = Depends(get_db)):
    return crud_city.get_all_cities(db)

@router.get("/{name}", response_model=CityOut, status_code=status.HTTP_200_OK)
def get_city_by_name(name: str, db: Session = Depends(get_db)):
    return crud_city.get_city_by_name(db, name)

@router.get("/{id}", response_model=CityOut, status_code=status.HTTP_200_OK)
def get_city_by_id(id: int, db: Session = Depends(get_db)):
    return crud_city.get_city_by_id(db, id)

@router.post("/", response_model=CityOut, status_code=status.HTTP_201_CREATED)
def create_city(payload: CityCreate, db: Session = Depends(get_db)):
    return crud_city.create_city(db, city_in=payload)

@router.put("/{name}", response_model=CityOut, status_code=status.HTTP_200_OK)
def update_city(id: int, payload: CityUpdate, db: Session = Depends(get_db)):
    return crud_city.update_city(db, city_id=id, city_in=payload)

@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_city(id: int, db: Session = Depends(get_db)):
    crud_city.delete_city(db, city_id=id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)