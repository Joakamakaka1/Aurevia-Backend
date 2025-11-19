from fastapi import APIRouter, Depends, Response, status
from typing import List
from sqlalchemy.orm import Session
from app.auth.deps import get_db
from app.service import trip as crud_trip
from app.schemas.trip import *

router = APIRouter(prefix="/v1/trip", tags=["Trip"])

@router.get("/", response_model=List[TripOut], status_code=status.HTTP_200_OK)
def get_all_trips(db: Session = Depends(get_db)):
    return crud_trip.get_all_trips(db)

@router.get("/{name}", response_model=TripOut, status_code=status.HTTP_200_OK)
def get_trip_by_name(name: str, db: Session = Depends(get_db)):
    return crud_trip.get_trip_by_name(db, name)

# TODO: Revisar si puede coger la entidad completa y no atributo por atributo
@router.post("/", response_model=TripOut, status_code = status.HTTP_201_CREATED)
def create_trip(payload: TripCreate, db: Session = Depends(get_db)):
    return crud_trip.create(db, trip_in=payload)

@router.put("/{name}", response_model=TripOut, status_code= status.HTTP_200_OK)
def update_trip(name: str, payload: TripUpdate, db: Session = Depends(get_db)):
    return crud_trip.update(db, trip_in=payload)

@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip_by_name(name: str, db: Session = Depends(get_db)):
    crud_trip.delete(db, name=name)
    return Response(status_code=status.HTTP_204_NO_CONTENT)