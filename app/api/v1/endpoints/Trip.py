from fastapi import APIRouter, Depends, Response, status
from typing import List
from sqlalchemy.orm import Session
from app.auth.deps import get_db
from app.service import trip as crud_trip
from app.schemas.trip import *
from app.core.exceptions import AppError

router = APIRouter(prefix="/v1/trip", tags=["Trip"])

@router.get("/", response_model=List[TripOut], status_code=status.HTTP_200_OK)
def get_all_trips(db: Session = Depends(get_db)):
    return crud_trip.get_all_trips(db)

@router.get("/name/{name}", response_model=TripOut, status_code=status.HTTP_200_OK)
def get_trip_by_name(name: str, db: Session = Depends(get_db)):
    trip = crud_trip.get_trip_by_name(db, name)
    if not trip:
        raise AppError(404, "TRIP_NOT_FOUND", "El viaje no existe")
    return trip

@router.post("/", response_model=TripOut, status_code=status.HTTP_201_CREATED)
def create_trip(payload: TripCreate, db: Session = Depends(get_db)):
    return crud_trip.create(db, trip_in=payload)

@router.put("/id/{trip_id}", response_model=TripOut, status_code=status.HTTP_200_OK)
def update_trip(trip_id: int, payload: TripUpdate, db: Session = Depends(get_db)):
    return crud_trip.update(db, trip_id=trip_id, trip_in=payload)

@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(trip_id: int, db: Session = Depends(get_db)):
    crud_trip.delete(db, id=id)
