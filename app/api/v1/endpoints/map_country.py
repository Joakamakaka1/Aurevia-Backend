from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.map_country import MapCountryRead
from app.service import map_country_service, map_service, user_service

router = APIRouter(prefix="/map-countries", tags=["Map Countries"])

@router.post("/me/countries/{country_id}", response_model=MapCountryRead, status_code=201)
def add_country_to_my_map(
    user_id: int,
    country_id: int,
    db: Session = Depends(get_db)
):
    
    user_map = map_service.get_map_by_user(db, user_id)
    
    if not user_map:
        user_map = map_service.create_map_for_user(db, user_id)
    
    map_country = map_country_service.add_country_to_map(db, user_map.id, country_id)
    
    # Actualizar métricas del mapa
    map_service.update_map_metrics(db, user_id)
    
    return map_country

@router.delete("/me/countries/{country_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_country_from_my_map(
    country_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar un país del mapa del usuario autenticado"""
    user_map = map_service.get_map_by_user(db, user_id)
    
    if not user_map:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Map not found")
    
    current_user = user_service.get_user_by_id(db, user_id)
    
    map_country_service.remove_country_from_map(db, user_map.id, country_id)
    
    # Actualizar métricas del mapa
    map_service.update_map_metrics(db, current_user.id)
    
    return None