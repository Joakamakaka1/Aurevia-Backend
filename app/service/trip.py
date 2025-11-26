from sqlalchemy.orm import Session
from app.db.models.trip import Trip
from app.core.exceptions import AppError
from app.schemas.trip import TripCreate, TripUpdate

def get_all_trips(db: Session) -> list[Trip]:
    return db.query(Trip).all()

def get_trip_by_name(db: Session, name: str) -> Trip | None:
    """

    ** Obtener un viaje por nombre **

    - Filtramos la tabla de Trip por el nombre del viaje
    - Igualamos al nombre que recibimos como parametro al nombre encontrado.
    
    """
    return db.query(Trip).filter(Trip.name == name).first()

def get_trip_by_id(db: Session, trip_id: int) -> Trip | None:
    """

    **  Obtener un viaje por ID  ** 

    - Filtramos la tabla de Trip por el nombre del viaje
    - Igualamos la id que recibimos como parametro a la id encontrada.

    """
    return db.query(Trip).filter(Trip.id == trip_id).first()

def get_trip_by_start_date_and_user(db: Session, start_date: str, user_id: int) -> Trip | None:
    """

    ** Obtener un viaje por fecha **

    - Filtramos la tabla de Trip por la fecha del viaje
    - Igualamos la fecha que recibimos como parametro a la fecha encontrada.
    - Usamos este metodo para verificar que la fecha del viaje no se repite, para no encontrar viajes con fechas de entrada duplicados
    - Tenemos en cuenta el usuario para verificar

    """
    return db.query(Trip).filter(Trip.start_date == start_date, Trip.user_id == user_id).first()

def create (db: Session, trip_in: TripCreate) -> Trip:
    " Verificamos si la fecha de entrada es posterior a la de salida "
    if(trip_in.start_date > trip_in.end_date):
        raise AppError(400, "INVALID_DATE", "La fecha de inicio no puede ser posterior a la fecha de fin")
        
    " Verificamos si el viaje ya existe con el metodo get_trip_by_start_date "
    if(get_trip_by_start_date_and_user(db, trip_in.start_date, trip_in.user_id)):
        raise AppError(400, "TRIP_ALREADY_EXISTS", "El viaje ya existe")
    
    trip = Trip(**trip_in.model_dump())
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip

def update (db: Session, trip_id: int, trip_in: TripUpdate) -> Trip:
    " Verificamos si el viaje existe "
    trip = get_trip_by_id(db, trip_id)
    if not trip:
        raise AppError(404, "TRIP_NOT_FOUND", "El viaje no existe")
    
    " Verificamos si la fecha de entrada es posterior a la de salida "
    if(trip_in.start_date > trip_in.end_date):
        raise AppError(400, "INVALID_DATE", "La fecha de inicio no puede ser posterior a la fecha de fin")
    
    for key, value in trip_in.model_dump().items():
        setattr(trip, key, value)
        
    db.commit()
    db.refresh(trip)
    return trip

def delete (db: Session, *, name: str) -> None:
    trip = Trip(name=name)
    db.delete(trip)
    db.commit()
    return None
