from fastapi import APIRouter, Depends, status
from typing import List
from app.service.city import CityService
from app.schemas.city import *
from app.core.exceptions import AppError
from app.api.deps import get_city_service

router = APIRouter(prefix="/v1/city", tags=["City"])

@router.get("/", response_model=List[CityOut], status_code=status.HTTP_200_OK)
def get_all_cities(service: CityService = Depends(get_city_service)):
    return service.get_all()

@router.get("/{name}", response_model=CityOut, status_code=status.HTTP_200_OK)
def get_city_by_name(name: str, service: CityService = Depends(get_city_service)):
    city = service.get_by_name(name)
    if not city:
        raise AppError(404, "CITY_NOT_FOUND", "La ciudad no existe")
    return city

@router.post("/", response_model=CityOut, status_code=status.HTTP_201_CREATED)
def create_city(payload: CityCreate, service: CityService = Depends(get_city_service)):
    return service.create(city_in=payload)

@router.put("/{id}", response_model=CityOut, status_code=status.HTTP_200_OK)
def update_city(id: int, payload: CityUpdate, service: CityService = Depends(get_city_service)):
    return service.update(city_id=id, city_in=payload)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_city(id: int, service: CityService = Depends(get_city_service)):
    service.delete(city_id=id)
