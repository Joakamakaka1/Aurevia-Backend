from fastapi import APIRouter, Depends, status
from typing import List
from app.service.trip import TripService
from app.schemas.trip import *
from app.core.exceptions import AppError
from app.api.deps import get_trip_service
from app.auth.deps import get_current_user, allow_admin

router = APIRouter(prefix="/v1/trip", tags=["Trip"])

@router.get("/", response_model=List[TripOut], status_code=status.HTTP_200_OK)
def get_all_trips(service: TripService = Depends(get_trip_service)):
    return service.get_all()

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
    return service.create(trip_in=payload)

@router.put("/id/{trip_id}", response_model=TripOut, status_code=status.HTTP_200_OK)
def update_trip(
    trip_id: int, 
    payload: TripUpdate, 
    service: TripService = Depends(get_trip_service),
    current_user = Depends(get_current_user)
):
    return service.update(trip_id=trip_id, trip_in=payload)

@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(
    trip_id: int, 
    service: TripService = Depends(get_trip_service),
    admin_user = Depends(allow_admin)
):
    service.delete(trip_id=trip_id)
