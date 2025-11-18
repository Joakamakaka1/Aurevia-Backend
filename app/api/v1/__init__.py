from fastapi import APIRouter
from .endpoints import user, trip, country

api_router = APIRouter()
api_router.include_router(user.router)
api_router.include_router(trip.router)
api_router.include_router(country.router)
