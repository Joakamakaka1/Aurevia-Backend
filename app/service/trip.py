# app/services/trip_service.py (ACTUALIZADO)
from datetime import datetime, date
from typing import List
from sqlalchemy.orm import Session
from app.db.models.trip import Trip
from app.db.models.map import Map
from app.service.map_country import add_country_to_map
from app.service.map import update_map_metrics, get_map_by_user, create_map_for_user
from app.core.exceptions import AppError

def getAllTrips(db: Session) -> List[Trip]: 
    return db.query(Trip).all()

def getAllTripsByUser(db: Session, user_id: int) -> List[Trip]:
    return db.query(Trip).filter(Trip.user_id == user_id).all()

def getAllTripsByDates(db: Session, start_date: str, end_date: str) -> List[Trip]:
    return db.query(Trip).filter(Trip.start_date >= start_date, Trip.end_date <= end_date).all()

def getTripById(db: Session, trip_id: int) -> Trip | None:
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not trip:
        raise AppError(404, "TRIP_NOT_FOUND", "Viaje no encontrado")
    return trip

def createTrip(db: Session, trip_data, user_id: int) -> Trip:
    """Crear un viaje y actualizar automáticamente el mapa"""
    
    # Validaciones
    notEmptyField(trip_data.get("title"), "title")
    notEmptyField(trip_data.get("description"), "description")
    notEmptyField(trip_data.get("start_date"), "start_date")
    notEmptyField(trip_data.get("end_date"), "end_date")
    notEmptyField(trip_data.get("country_id"), "country_id")

    start = parse_date(trip_data.get("start_date"), "start_date")
    end = parse_date(trip_data.get("end_date"), "end_date")
    
    if start > end:
        raise AppError(400, "START_DATE_INVALID", "La fecha de inicio no puede ser posterior a la fecha de fin")

    # Crear el viaje
    data = dict(trip_data)
    data["start_date"] = start
    data["end_date"] = end
    data["user_id"] = user_id
    
    trip = Trip(**data)
    db.add(trip)
    db.flush()  # Para obtener el trip_id sin hacer commit
    
    user_map = get_map_by_user(db, user_id)
    
    # Si el usuario no tiene mapa, crearlo
    if not user_map:
        user_map = create_map_for_user(db, user_id)
    
    # Añadir el país al mapa (si no existe ya)
    add_country_to_map(db, user_map.id, trip_data.get("country_id"))
    
    # Actualizar métricas del mapa
    update_map_metrics(db, user_id)
    
    db.commit()
    db.refresh(trip)
    return trip

def updateTripById(db: Session, trip_id: int, trip_data, user_id: int) -> Trip:
    """Actualizar un viaje"""
    trip = getTripById(db, trip_id)
    
    # Verificar que el viaje pertenece al usuario
    if trip.user_id != user_id:
        raise AppError(403, "FORBIDDEN", "No tienes permiso para actualizar este viaje")
    
    # Actualizar campos si están presentes
    if trip_data.get("title"):
        trip.title = trip_data.get("title")
    if trip_data.get("description"):
        trip.description = trip_data.get("description")
    if trip_data.get("start_date"):
        trip.start_date = parse_date(trip_data.get("start_date"), "start_date")
    if trip_data.get("end_date"):
        trip.end_date = parse_date(trip_data.get("end_date"), "end_date")
    
    # Si cambia el país, actualizar el mapa
    if trip_data.get("country_id") and trip_data.get("country_id") != trip.country_id:
        old_country_id = trip.country_id
        trip.country_id = trip_data.get("country_id")
        
        # Añadir nuevo país al mapa
        user_map = get_map_by_user(db, user_id)
        add_country_to_map(db, user_map.id, trip.country_id)
        
        # Verificar si hay otros viajes al país antiguo
        other_trips = db.query(Trip).filter(
            Trip.user_id == user_id,
            Trip.country_id == old_country_id,
            Trip.trip_id != trip_id
        ).count()
    
        # Actualizar métricas
        update_map_metrics(db, user_id)
    
    db.commit()
    db.refresh(trip)
    return trip
    
def deleteTripById(db: Session, trip_id: int, user_id: int):
    """Eliminar un viaje y actualizar el mapa si es necesario"""
    trip = getTripById(db, trip_id)
    
    # Verificar que el viaje pertenece al usuario
    if trip.user_id != user_id:
        raise AppError(403, "FORBIDDEN", "No tienes permiso para eliminar este viaje")
    
    country_id = trip.country_id
    
    # Eliminar el viaje
    db.delete(trip)
    db.flush()
    
    # Verificar si hay otros viajes a ese país
    other_trips = db.query(Trip).filter(
        Trip.user_id == user_id,
        Trip.country_id == country_id
    ).count()
    
    # Actualizar métricas del mapa
    update_map_metrics(db, user_id)
    
    db.commit()

# Funciones auxiliares (mantener igual)
def notEmptyField(value, field_name: str):
    if not value:
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