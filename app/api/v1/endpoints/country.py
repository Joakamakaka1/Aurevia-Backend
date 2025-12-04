from fastapi import APIRouter, Depends, status
from typing import List
from app.service.country import CountryService
from app.schemas.country import *
from app.core.exceptions import AppError
from app.api.deps import get_country_service

router = APIRouter(prefix="/v1/country", tags=["Country"])

@router.get("/", response_model=List[CountryOut], status_code=status.HTTP_200_OK)
def get_all_countries(service: CountryService = Depends(get_country_service)):
    return service.get_all()

@router.get("/{name}", response_model=CountryOut, status_code=status.HTTP_200_OK)
def get_country_by_name(name: str, service: CountryService = Depends(get_country_service)):
    country = service.get_by_name(name)
    if not country:
        raise AppError(404, "COUNTRY_NOT_FOUND", "El país no existe")
    return country

@router.post("/", response_model=CountryOut, status_code=status.HTTP_201_CREATED)
def create_country(payload: CountryCreate, service: CountryService = Depends(get_country_service)):
    return service.create(country_in=payload)

@router.put("/{id}", response_model=CountryOut, status_code=status.HTTP_200_OK)
def update_country(id: int, payload: CountryUpdate, service: CountryService = Depends(get_country_service)):
    return service.update(country_id=id, country_in=payload)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_country(id: int, service: CountryService = Depends(get_country_service)):
    service.delete(country_id=id)
