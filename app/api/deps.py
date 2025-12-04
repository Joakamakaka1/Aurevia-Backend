from fastapi import Depends
from sqlalchemy.orm import Session
from app.auth.deps import get_db
from app.service.user import UserService
from app.service.trip import TripService
from app.service.country import CountryService
from app.service.city import CityService
from app.service.comment import CommentService

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

def get_trip_service(db: Session = Depends(get_db)) -> TripService:
    return TripService(db)

def get_country_service(db: Session = Depends(get_db)) -> CountryService:
    return CountryService(db)

def get_city_service(db: Session = Depends(get_db)) -> CityService:
    return CityService(db)

def get_comment_service(db: Session = Depends(get_db)) -> CommentService:
    return CommentService(db)
