from fastapi import APIRouter, Depends, Response, status
from typing import List
from sqlalchemy.orm import Session
from app.auth.deps import get_db
from app.schemas.country import *
from app.service import country as crud_country

router = APIRouter(prefix="/v1/country", tags=["Country"])

@router.get("/", response_model=List[CountryOut], status_code=status.HTTP_200_OK)
def get_all_countries(db: Session = Depends(get_db)):
    return crud_country.get_all_countries(db)

@router.get("/{name}", response_model=CountryUpdate, status_code=status.HTTP_200_OK)
def get_country_by_name(name: str, db: Session = Depends(get_db)):
    return crud_country.get_country_by_name(db, name)

@router.post("/", response_model=CountryCreate, status_code=status.HTTP_201_CREATED)
def create_country(payload: CountryCreate, db: Session = Depends(get_db)):
    return crud_country.create_country(db, payload.name)

@router.put("/{name}", response_model=CountryUpdate, status_code=status.HTTP_200_OK)
def update_country(payload: CountryUpdate, db: Session = Depends(get_db)):
    return crud_country.update_country_by_name(db, payload.name)

@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_country(name: str, db: Session = Depends(get_db)):
    crud_country.delete_country_by_name(db, name)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


                     