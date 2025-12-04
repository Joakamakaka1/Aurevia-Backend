from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models.trip import Trip
from app.schemas.trip import TripCreate, TripUpdate
from app.core.exceptions import AppError
from app.core.constants import ErrorCode
from app.core.decorators import transactional
from app.repository.trip import TripRepository
from app.repository.user import UserRepository
from app.repository.country import CountryRepository

class TripService:

    '''
    Servicio que maneja la lógica de negocio de viajes.
    
    Responsabilidades:
    - Validación de fechas (start_date < end_date)
    - Validación de integridad referencial (user_id, country_id)
    - Validación de unicidad (un viaje por usuario por fecha de inicio)
    - CRUD con validaciones en múltiples capas
    '''
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = TripRepository(db)
        self.user_repo = UserRepository(db)
        self.country_repo = CountryRepository(db)

    def get_all(self) -> List[Trip]:
        return self.repo.get_all()

    def get_by_name(self, name: str) -> Optional[Trip]:
        return self.repo.get_by_name(name)

    def get_by_id(self, trip_id: int) -> Optional[Trip]:
        return self.repo.get_by_id(trip_id)

    def validate_trip_dates(self, start_date: str, end_date: str) -> None:
        """Valida que start_date sea anterior a end_date"""
        if start_date > end_date:
            raise AppError(400, ErrorCode.INVALID_DATE, "La fecha de inicio no puede ser posterior a la fecha de fin")

    @transactional
    def create(self, trip_in: TripCreate) -> Trip:
        '''
        Crea un nuevo viaje aplicando validaciones en 4 etapas:
        
        1. Validaciones de Negocio: Fechas lógicas (inicio < fin)
        2. Validaciones de Integridad: Existencia de user_id y country_id
        3. Validaciones de Unicidad: No duplicar viajes en misma fecha
        4. Creación: Persistir en base de datos
        '''
        # 1. Validaciones de Negocio (Fechas)
        self.validate_trip_dates(trip_in.start_date, trip_in.end_date)
        
        # 2. Validaciones de Integridad (Foreign Keys)
        if not self.user_repo.get_by_id(trip_in.user_id):
            raise AppError(404, ErrorCode.USER_NOT_FOUND, f"El usuario con ID {trip_in.user_id} no existe")
        
        if not self.country_repo.get_by_id(trip_in.country_id):
            raise AppError(404, ErrorCode.COUNTRY_NOT_FOUND, f"El país con ID {trip_in.country_id} no existe")
        
        # 3. Validaciones de Unicidad
        if self.repo.get_by_start_date_and_user(trip_in.start_date, trip_in.user_id):
            raise AppError(400, ErrorCode.TRIP_ALREADY_EXISTS, "El viaje ya existe para este usuario en esa fecha")
        
        # 4. Creación
        return self.repo.create(trip_in)

    @transactional
    def update(self, trip_id: int, trip_in: TripUpdate) -> Trip:
        trip = self.repo.get_by_id(trip_id)
        
        if not trip:
            raise AppError(404, ErrorCode.TRIP_NOT_FOUND, "El viaje no existe")
        
        # Convertir a dict solo con campos no-None
        trip_data = trip_in.model_dump(exclude_unset=True)
        
        # Validar fechas si se están actualizando
        start_date = trip_data.get('start_date', trip.start_date)
        end_date = trip_data.get('end_date', trip.end_date)
        self.validate_trip_dates(start_date, end_date)
        
        return self.repo.update(trip, trip_data)

    @transactional
    def delete(self, trip_id: int) -> None:
        trip = self.repo.get_by_id(trip_id)
        
        if not trip:
            raise AppError(404, ErrorCode.TRIP_NOT_FOUND, "El viaje no existe")
        
        self.repo.delete(trip)
