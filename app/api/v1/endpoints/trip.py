from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.orm import Session
from app.auth.deps import get_db
from app.service import trip as crud_trip
from app.schemas.trip import TripCreate, TripBase

router = APIRouter(prefix="/v1/trips", tags=["Trips"])

@router.get("/", response_model=List[TripBase], status_code=status.HTTP_200_OK)
def get_AllTrips():
    return crud_trip.getAllTrips()

@router.get("/{trip_id}", response_model=TripBase, status_code=status.HTTP_200_OK)
def get_trip_by_id(trip_id: int):
    return crud_trip.getTripById(trip_id)

@router.get("/user/{user_id}", response_model=List[TripBase], status_code=status.HTTP_200_OK)
def get_trips_by_user(user_id: int):
    return crud_trip.getAllTripsByUser(user_id)

@router.get("/country/{country_id}", response_model=List[TripBase], status_code=status.HTTP_200_OK)
def get_trips_by_country(country_id: str):
    return crud_trip.getAllTripsByCountry(country_id)

@router.get("/dates/{start_date}/{end_date}", response_model=List[TripBase], status_code=status.HTTP_200_OK)
def get_trips_by_dates(start_date: str, end_date: str):
    return crud_trip.getAllTripsByDates(start_date, end_date)

@router.post("/", response_model=TripCreate, status_code=status.HTTP_201_CREATED)
def create_trip(payload: TripCreate, db: Session = Depends(get_db)):
    return crud_trip.createTrip(db, trip_data=payload.dict())

# TODO: Implementarlos
@router.put("/{trip_id}", response_model=TripBase)
def update_trip():
    pass

@router.delete("/{trip_id}", response_model=TripBase)
def delete_trip():
    pass