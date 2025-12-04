from fastapi import APIRouter
from .endpoints import user, trip, country, city, comment, healthy

api_router = APIRouter()
api_router.include_router(user.router)
api_router.include_router(trip.router)
api_router.include_router(country.router)
api_router.include_router(city.router)
api_router.include_router(comment.router)
api_router.include_router(healthy.router)
