from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.map import MapRead
from app.schemas.map_country import MapCountryWithCountry
from app.service import map_service, map_country_service, user_service
from typing import List

router = APIRouter(prefix="/maps", tags=["Maps"])

@router.get("/me", response_model=MapRead, status_code=status.HTTP_200_OK)
def get_my_map(user_id: int, db: Session = Depends(get_db)):
   user = user_service.get_user_by_id(db, user_id=user_id)
   return map_service.get_map_by_user(db, user.id)

@router.post("/me", response_model=MapRead, status_code=status.HTTP_201_CREATED)
def create_my_map(user_id: int,db: Session = Depends(get_db)):
    return map_service.create_map_for_user(db, user_id)

@router.get("/me/countries", response_model=List[MapCountryWithCountry], status_code=status.HTTP_200_OK)
def get_my_visited_countries(user_id: int, db: Session = Depends(get_db)):
    return map_country_service.get_map_countries_by_user(db, user_id)

@router.get("/me/complete", response_model=dict, status_code=status.HTTP_200_OK)
def get_my_complete_map(user_id: int, db: Session = Depends(get_db)):
    result = map_service.get_map_with_countries(db, user_id=user_id)
    
    return {
        "map": {
            "id": result["map"].id,
            "countries_visited": result["map"].countries_visited,
            "percent_world_visited": result["map"].percent_world_visited,
            "map_image_url": result["map"].map_image_url,
            "last_updated": result["map"].last_updated
        },
        "visited_countries": [
            {
                "country_id": mc.country_id,
                "country_name": mc.country.name,
                "country_iso_code": mc.country.iso_code,
                "first_visited": mc.first_visited,
                "visit_count": mc.visit_count,
                "last_visit": mc.last_visit
            }
            for mc in result["visited_countries"]
        ]
    }

@router.put("/me/refresh", response_model=MapRead, status_code=status.HTTP_200_OK)
def refresh_my_map_metrics(user_id: int, db: Session = Depends(get_db)):
    return map_service.update_map_metrics(db, user_id)