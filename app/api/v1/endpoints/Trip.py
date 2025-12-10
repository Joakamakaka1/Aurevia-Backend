from fastapi import APIRouter, Depends, status
from typing import List
from app.service.trip import TripService
from app.schemas.trip import *
from app.core.exceptions import AppError
from app.api.deps import get_trip_service
from app.auth.deps import get_current_user, allow_admin, check_self_or_admin

router = APIRouter(prefix="/v1/trip", tags=["Trip"])

@router.get("/", response_model=List[TripOut], status_code=status.HTTP_200_OK)
def get_all_trips(
    skip: int = 0,
    limit: int = 50,
    service: TripService = Depends(get_trip_service)
):
    return service.get_all(skip=skip, limit=limit)

@router.get("/name/{name}", response_model=TripOut, status_code=status.HTTP_200_OK)
def get_trip_by_name(name: str, service: TripService = Depends(get_trip_service)):
    trip = service.get_by_name(name)
    if not trip:
        raise AppError(404, "TRIP_NOT_FOUND", "El viaje no existe")
    return trip

@router.get("/id/{trip_id}", response_model=TripOut, status_code=status.HTTP_200_OK)
def get_trip_by_id(trip_id: int, service: TripService = Depends(get_trip_service)):
    trip = service.get_by_id(trip_id)
    if not trip:
        raise AppError(404, "TRIP_NOT_FOUND", "El viaje no existe")
    return trip

@router.post("/", response_model=TripOut, status_code=status.HTTP_201_CREATED)
def create_trip(
    payload: TripCreate, 
    service: TripService = Depends(get_trip_service),
    current_user = Depends(get_current_user)
):
    # Forzar que el usuario que crea el viaje sea el mismo del token
    if payload.user_id != current_user.user_id:
        payload.user_id = current_user.user_id

    return service.create(trip_in=payload)

@router.put("/id/{trip_id}", response_model=TripOut, status_code=status.HTTP_200_OK)
def update_trip(
    trip_id: int, 
    payload: TripUpdate, 
    service: TripService = Depends(get_trip_service),
    current_user = Depends(get_current_user)
):
    trip = service.get_by_id(trip_id)
    if not trip:
        raise AppError(404, "TRIP_NOT_FOUND", "El viaje no existe")
    
    # Validar que sea dueño o admin
    check_self_or_admin(current_user, trip.user_id)
    
    return service.update(trip_id=trip_id, trip_in=payload)

@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(
    trip_id: int, 
    service: TripService = Depends(get_trip_service),
    current_user = Depends(get_current_user)
):
    trip = service.get_by_id(trip_id)
    if not trip:
        raise AppError(404, "TRIP_NOT_FOUND", "El viaje no existe")
        
    # Validar que sea dueño o admin
    check_self_or_admin(current_user, trip.user_id)
    
    service.delete(trip_id=trip_id)
