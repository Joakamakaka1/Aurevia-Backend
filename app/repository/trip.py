from sqlalchemy.orm import Session, joinedload
from app.db.models.trip import Trip
from app.schemas.trip import TripCreate, TripUpdate
from typing import List, Optional

class TripRepository:
    '''
    Repositorio de Trips - Capa de acceso a datos.
    
    Todas las consultas usan joinedload para cargar country y comments
    de forma eficiente (eager loading) y evitar el problema N+1.
    '''
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Trip]:
        return (
            self.db.query(Trip)
            .options(joinedload(Trip.country), joinedload(Trip.comments))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id(self, trip_id: int) -> Optional[Trip]:
        return (
            self.db.query(Trip)
            .options(joinedload(Trip.country), joinedload(Trip.comments))
            .filter(Trip.id == trip_id)
            .first()
        )

    def get_by_name(self, name: str) -> Optional[Trip]:
        return (
            self.db.query(Trip)
            .options(joinedload(Trip.country), joinedload(Trip.comments))
            .filter(Trip.name == name)
            .first()
        )

    def get_by_start_date_and_user(self, start_date: str, user_id: int) -> Optional[Trip]:
        return (
            self.db.query(Trip)
            .filter(Trip.start_date == start_date, Trip.user_id == user_id)
            .first()
        )

    def create(self, trip_in: TripCreate) -> Trip:
        # Nota: No hacemos commit aquí, lo maneja el servicio con el decorador @transactional
        trip = Trip(**trip_in.model_dump())
        self.db.add(trip)
        return trip

    def update(self, trip: Trip, trip_data: dict) -> Trip:
        for key, value in trip_data.items():
            if value is not None:
                setattr(trip, key, value)
        return trip

    def delete(self, trip: Trip) -> None:
        self.db.delete(trip)
