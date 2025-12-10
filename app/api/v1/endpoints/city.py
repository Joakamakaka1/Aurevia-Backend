from fastapi import APIRouter, Depends, status
from typing import List
from app.service.city import CityService
from app.schemas.city import *
from app.core.exceptions import AppError
from app.api.deps import get_city_service
from app.auth.deps import get_current_user, allow_admin

router = APIRouter(prefix="/v1/city", tags=["City"])

@router.get("/", response_model=List[CityOut], status_code=status.HTTP_200_OK)
def get_all_cities(service: CityService = Depends(get_city_service)):
    return service.get_all()

@router.get("/name/{name}", response_model=CityOut, status_code=status.HTTP_200_OK)
def get_city_by_name(name: str, service: CityService = Depends(get_city_service)):
    city = service.get_by_name(name)
    if not city:
        raise AppError(404, "CITY_NOT_FOUND", "La ciudad no existe")
    return city

@router.get("/country/{country_code}", response_model=List[CityOut], status_code=status.HTTP_200_OK)
def get_cities_by_country(country_code: str, service: CityService = Depends(get_city_service)):
    """
    Obtiene todas las ciudades de un país específico por su código ISO (Alpha-2 o Alpha-3).
    """
    cities = service.get_by_country_code(country_code)
    # Si no hay ciudades, devolvemos lista vacía con 200 OK, no 404
    return cities

@router.post("/populate", status_code=status.HTTP_200_OK)
async def populate_cities(
    country_code: str = None, 
    limit: int = 50,
    service: CityService = Depends(get_city_service)
):
    """
    Puebla ciudades desde GeoNames API.
    Si se especifica country_code (ej: 'ES'), solo para ese país.
    Si no, intenta poblar para TODOS los países (puede tardar).
    """
    if country_code:
        return await service.populate_from_api(country_code, limit=limit)
    else:
        return await service.populate_all_countries_cities(limit_per_country=limit)

@router.post("/", response_model=CityOut, status_code=status.HTTP_201_CREATED)
def create_city(
    payload: CityCreate, 
    service: CityService = Depends(get_city_service),
    current_user = Depends(get_current_user)
):
    return service.create(city_in=payload)

@router.put("/{id}", response_model=CityOut, status_code=status.HTTP_200_OK)
def update_city(
    id: int, 
    payload: CityUpdate, 
    service: CityService = Depends(get_city_service),
    current_user = Depends(get_current_user)
):
    return service.update(city_id=id, city_in=payload)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_city(
    id: int, 
    service: CityService = Depends(get_city_service),
    admin_user = Depends(allow_admin)
):
    service.delete(city_id=id)
