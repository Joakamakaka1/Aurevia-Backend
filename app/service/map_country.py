                                                                                                                    # app/services/map_country_service.py
from sqlalchemy.orm import Session
from app.db.models.map_country import MapCountry
from app.db.models.map import Map
from app.db.models.country import Country
from app.core.exceptions import AppError
from datetime import datetime, timezone
from typing import List, Optional

def add_country_to_map(db: Session, map_id: int, country_id: int) -> MapCountry:
    """Añade un país al mapa del usuario (si no existe ya)"""
    
    # Verificar que el mapa existe
    user_map = db.query(Map).filter(Map.id == map_id).first()
    if not user_map:
        raise AppError(404, "MAP_NOT_FOUND", "Mapa no encontrado")
    
    # Verificar que el país existe
    country = db.query(Country).filter(Country.id == country_id).first()
    if not country:
        raise AppError(404, "COUNTRY_NOT_FOUND", "País no encontrado")
    
    # Verificar si ya existe la relación
    existing = db.query(MapCountry).filter(
        MapCountry.map_id == map_id,
        MapCountry.country_id == country_id
    ).first()
    
    if existing:
        # Ya existe, incrementar contador de visitas (Ha visitado el país mas de una vez)
        existing.visit_count += 1
        existing.last_visit = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
        return existing
    
    # Crear nueva relación
    map_country = MapCountry(
        map_id=map_id,
        country_id=country_id
    )
    db.add(map_country)
    db.commit()
    db.refresh(map_country)
    return map_country

def get_countries_by_map(db: Session, map_id: int) -> List[MapCountry]:
    """Obtiene todos los países visitados de un mapa"""
    mapCountry = db.query(MapCountry).filter(MapCountry.map_id == map_id).first()
    if not mapCountry:
        raise AppError(404, "MAP_NOT_FOUND", "Mapa no encontrado")
    
    return db.query(MapCountry).filter(MapCountry.map_id == map_id).all()

def remove_country_from_map(db: Session, map_id: int, country_id: int):
    """Elimina un país de un mapa del usuario"""
    map_country = db.query(MapCountry).filter(
        MapCountry.map_id == map_id,
        MapCountry.country_id == country_id
    ).first()
    
    if not map_country:
        raise AppError(404, "MAP_COUNTRY_NOT_FOUND", "Relación mapa-país no encontrada")
    
    db.delete(map_country)
    db.commit()