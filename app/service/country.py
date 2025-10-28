from sqlalchemy.orm import Session
from app.db.models.country import Country
from app.core.exceptions import AppError
from typing import List
from typing import Optional

def get_all_countries(db: Session) -> List[Country]: 
    country = db.query(Country).first()
    if not country:
        raise AppError(404, "COUNTRY_NOT_FOUND", "Países no encontrado")
    
    return db.query(Country).all()

def get_country_by_id(db: Session, country_id: int) -> Optional[Country]:
    """Obtener un país por ID"""
    country = db.query(Country).filter(Country.id == country_id).first()
    if not country:
        raise AppError(404, "COUNTRY_NOT_FOUND", "País no encontrado")
    
    return country

def get_country_by_iso_code(db: Session, iso_code: str) -> Optional[Country]:
    """Obtener un país por código ISO"""
    country = db.query(Country).filter(Country.iso_code == iso_code.upper()).first()
    if not country:
        raise AppError(404, "COUNTRY_NOT_FOUND", f"País con código ISO '{iso_code}' no encontrado")
    
    return country

def search_countries(db: Session, search_term: str) -> List[Country]:
    """Buscar países por nombre"""
    country = db.query(Country).filter(Country.name == search_term).first()
    if not country:
        raise AppError(404, "COUNTRY_NOT_FOUND", f"País '{search_term}' no encontrado")
    
    return db.query(Country).filter(
        Country.name.ilike(f"%{search_term}%")
    ).all()

def get_countries_by_continent(db: Session, continent: str) -> List[Country]:
    """Obtener países por continente"""
    country = db.query(Country).filter(Country.continent == continent).first()
    if not country:
        raise AppError(404, "COUNTRY_NOT_FOUND", f"Países con continente '{continent}' no encontrado")
    
    return db.query(Country).filter(Country.continent == continent).all()

