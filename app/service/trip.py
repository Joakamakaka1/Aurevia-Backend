from datetime import datetime, date
from typing import List
from sqlalchemy.orm import Session
from app.db.models.trip import Trip
from app.core.exceptions import AppError

def getAllTrips(db: Session) -> List[Trip]: 
    return db.query(Trip).all()

def getAllTripsByUser(db: Session, user_id: int) -> List[Trip]:
    return db.query(Trip).filter(Trip.user_id == user_id).all()

def getAllTripsByCountry(db: Session, country_id: str) -> List[Trip]:
    return db.query(Trip).filter(Trip.country_id == country_id).all()

def getAllTripsByDates(db: Session, start_date: str, end_date: str) -> List[Trip]:
    return db.query(Trip).filter(Trip.start_date >= start_date, Trip.end_date <= end_date).all()

def getTripById(db: Session, trip_id: int) -> Trip | None:
    return db.query(Trip).filter(Trip.trip_id == trip_id).first()

# TODO: Validar que el viaje no exista ya para el mismo usuario
def createTrip(db: Session, trip_data) -> Trip:

    notEmptyField(trip_data.get("title"), "title")
    notEmptyField(trip_data.get("description"), "description")
    notEmptyField(trip_data.get("start_date"), "start_date")
    notEmptyField(trip_data.get("end_date"), "end_date")

    start = parse_date(trip_data.get("start_date"), "start_date")
    end = parse_date(trip_data.get("end_date"), "end_date")
    
    if start > end:
        raise AppError(400, "START_DATE_INVALID", "La fecha de inicio no puede ser posterior a la fecha de fin")

    if start < end:
        raise AppError(400, "END_DATE_INVALID", "La fecha de fin no puede ser anterior a la fecha de inicio")

    data = dict(trip_data)
    data["start_date"] = start
    data["end_date"] = end

    trip = Trip(**data)
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip

def updateTripById(trip_id: int, trip_data):
    pass
    
def deleteTripById(trip_id: int):
    pass

def notEmptyField(value, field_name: str):
    if not value or value.strip() == "":
        raise AppError(400, f"{field_name.upper()}_EMPTY", f"El {field_name} no puede estar vacío")
    return value

def parse_date(value, field_name: str, fmt: str = "%Y-%m-%d") -> date:
    if value is None:
        raise AppError(400, "DATE_MISSING", f"{field_name} no puede estar vacío")
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    try:
        return datetime.strptime(value, fmt).date()
    except Exception:
        raise AppError(400, "DATE_FORMAT_INVALID", f"{field_name} debe tener formato {fmt} (ej. 2025-10-17)")
