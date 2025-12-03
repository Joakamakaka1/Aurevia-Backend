from fastapi import APIRouter, Depends, Response, status
from typing import List
from sqlalchemy.orm import Session
from app.auth.deps import get_db
from app.schemas.country import *
from app.service import country as crud_country
from app.core.exceptions import AppError

router = APIRouter(prefix="/v1/country", tags=["Country"])

@router.get("/", response_model=List[CountryOut], status_code=status.HTTP_200_OK)
def get_all_countries(db: Session = Depends(get_db)):
    return crud_country.get_all_countries(db)

@router.get("/name/{name}", response_model=CountryOut, status_code=status.HTTP_200_OK)
def get_country_by_name(name: str, db: Session = Depends(get_db)):
    country = crud_country.get_country_by_name(db, name)
    if not country:
        raise AppError(404, "COUNTRY_NOT_FOUND", "El país no existe")
    return country

@router.get("/id/{id}", response_model=CountryOut, status_code=status.HTTP_200_OK)
def get_country_by_id(id: int, db: Session = Depends(get_db)):
    country = crud_country.get_country_by_id(db, id)
    if not country:
        raise AppError(404, "COUNTRY_NOT_FOUND", "El país no existe")
    return country

@router.post("/", response_model=CountryOut, status_code=status.HTTP_201_CREATED)
def create_country(payload: CountryCreate, db: Session = Depends(get_db)):
    return crud_country.create_country(db, country_in=payload)

@router.put("/{id}", response_model=CountryOut, status_code=status.HTTP_200_OK)
def update_country(id: int, payload: CountryUpdate, db: Session = Depends(get_db)):
    return crud_country.update_country(db, country_id=id, country_in=payload)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_country(id: int, db: Session = Depends(get_db)):
    crud_country.delete_country(db, country_id=id)
