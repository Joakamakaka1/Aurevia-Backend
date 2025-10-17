from sqlalchemy.orm import Session
from app.db.models.map import Map
from app.db.models.trip import Trip
from app.db.models.country import Country
from app.core.exceptions import AppError
from datetime import datetime, timezone

def get_map_by_user(db: Session, user_id: int):
    return db.query(Map).filter(Map.user_id == user_id).first()

def create_map_for_user(db: Session, user_id: int) -> Map:
    existing_map = get_map_by_user(db, user_id)
    if existing_map:
        raise AppError(409, "MAP_ALREADY_EXISTS", "Map already exists for this user")
    
    new_map = Map(user_id=user_id)
    db.add(new_map)
    db.commit()
    db.refresh(new_map)
    return new_map

def update_map_metrics(db: Session, user_id: int, countries_visited: int, percent_world_visited: float) -> Map:
    user_map = get_map_by_user(db, user_id)
    if not user_map:
        raise AppError(404, "MAP NOT FOUND", "Map not found for the given user ID")
        
    # Contar países únicos visitados
    trips = db.query(Trip).filter(Trip.user_id == user_id).all()
    country_ids = {t.country_id for t in trips}
    countries_visited = len(country_ids)

    # Calcular el total de países disponibles 
    total_countries = db.query(Country).count()
    percent_world_visited = (countries_visited / total_countries * 100) if total_countries > 0 else 0.0

    # Actualizar los campos del mapa
    user_map.countries_visited = countries_visited
    user_map.percent_world_visited =  percent_world_visited
    user_map.last_updated = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user_map)
    return user_map