from sqlalchemy.orm import Session
from app.schemas.trip import TripCreate, TripUpdate
from app.core.exceptions import AppError
from app.core.constants import ErrorCode
from app.core.decorators import transactional
from app.repository.trip import TripRepository
from app.service.user import get_user_by_id
from app.service.country import get_country_by_id
from app.db.models.trip import Trip

# Ya no necesitamos funciones sueltas para validaciones de longitud
# porque Pydantic se encarga de eso en el Schema.

def get_all_trips(db: Session) -> list[Trip]:
    repo = TripRepository(db)
    return repo.get_all()

def get_trip_by_name(db: Session, name: str) -> Trip | None:
    repo = TripRepository(db)
    return repo.get_by_name(name)

def get_trip_by_id(db: Session, trip_id: int) -> Trip | None:
    repo = TripRepository(db)
    return repo.get_by_id(trip_id)

def validate_trip_dates(start_date: str, end_date: str) -> None:
    """Valida que start_date sea anterior a end_date"""
    if start_date > end_date:
        raise AppError(400, ErrorCode.INVALID_DATE, "La fecha de inicio no puede ser posterior a la fecha de fin")

@transactional
def create(db: Session, trip_in: TripCreate) -> Trip:
    repo = TripRepository(db)
    
    # 1. Validaciones de Negocio (Fechas)
    validate_trip_dates(trip_in.start_date, trip_in.end_date)
    
    # 2. Validaciones de Integridad (Foreign Keys)
    if not get_user_by_id(db, trip_in.user_id):
        raise AppError(404, ErrorCode.USER_NOT_FOUND, f"El usuario con ID {trip_in.user_id} no existe")
    
    if not get_country_by_id(db, trip_in.country_id):
        raise AppError(404, ErrorCode.COUNTRY_NOT_FOUND, f"El país con ID {trip_in.country_id} no existe")
    
    # 3. Validaciones de Unicidad
    if repo.get_by_start_date_and_user(trip_in.start_date, trip_in.user_id):
        raise AppError(400, ErrorCode.TRIP_ALREADY_EXISTS, "El viaje ya existe para este usuario en esa fecha")
    
    # 4. Creación (El commit lo hace el decorador)
    return repo.create(trip_in)

@transactional
def update(db: Session, trip_id: int, trip_in: TripUpdate) -> Trip:
    repo = TripRepository(db)
    trip = repo.get_by_id(trip_id)
    
    if not trip:
        raise AppError(404, ErrorCode.TRIP_NOT_FOUND, "El viaje no existe")
    
    # Convertir a dict solo con campos no-None
    trip_data = trip_in.model_dump(exclude_unset=True)
    
    # Validar fechas si se están actualizando
    start_date = trip_data.get('start_date', trip.start_date)
    end_date = trip_data.get('end_date', trip.end_date)
    validate_trip_dates(start_date, end_date)
    
    return repo.update(trip, trip_data)

@transactional
def delete(db: Session, *, id: int) -> None:
    repo = TripRepository(db)
    trip = repo.get_by_id(id)
    
    if not trip:
        raise AppError(404, ErrorCode.TRIP_NOT_FOUND, "El viaje no existe")
    
    repo.delete(trip)
    # El commit lo hace el decorador


