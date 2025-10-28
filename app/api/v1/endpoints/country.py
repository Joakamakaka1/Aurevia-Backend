from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.country import CountryBase
from app.service import country_service

router = APIRouter(prefix="/v1/countries", tags=["Countries"])

@router.get("/", response_model=List[CountryBase], status_code=status.HTTP_200_OK)
def get_all_countries(db: Session = Depends(get_db)):
    return country_service.get_all_countries(db)

@router.get("/search", response_model=List[CountryBase])
def search_countries(
    q: str = Query(..., min_length=2, description="Término de búsqueda"),
    db: Session = Depends(get_db)
):
    return country_service.search_countries(db, q)

@router.get("/continent/{continent}", response_model=List[CountryBase])
def get_countries_by_continent(continent: str, db: Session = Depends(get_db)):
    return country_service.get_countries_by_continent(db, continent)

@router.get("/{country_id}", response_model=CountryBase)
def get_country_by_id(country_id: int, db: Session = Depends(get_db)):
    return country_service.get_country_by_id(db, country_id)

@router.get("/iso/{iso_code}", response_model=CountryBase)
def get_country_by_iso(iso_code: str,db: Session = Depends(get_db)):
    return country_service.get_country_by_iso_code(db, iso_code)