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

def validate_trip_dates(start_date: str, end_date: str) -> None:
    """Valida que start_date sea anterior a end_date"""
    if start_date > end_date:
        raise AppError(400, "INVALID_DATE", "La fecha de inicio no puede ser posterior a la fecha de fin")

def validate_trip_name_length(name: str) -> None:
    """Valida longitud del nombre del viaje"""
    if len(name) < 3:
        raise AppError(400, "NAME_TOO_SHORT", "El nombre del viaje debe tener al menos 3 caracteres")
    if len(name) > 100:
        raise AppError(400, "NAME_TOO_LONG", "El nombre del viaje no puede tener más de 100 caracteres")

def validate_trip_description_length(description: str) -> None:
    """Valida longitud de la descripción"""
    if len(description) < 10:
        raise AppError(400, "DESCRIPTION_TOO_SHORT", "La descripción debe tener al menos 10 caracteres")
    if len(description) > 500:
        raise AppError(400, "DESCRIPTION_TOO_LONG", "La descripción no puede tener más de 500 caracteres")

def create(db: Session, trip_in: TripCreate) -> Trip:
    # Validar fechas primero
    validate_trip_dates(trip_in.start_date, trip_in.end_date)
    
    # Validar longitud de campos (también validado en schema, pero mantenemos por si acaso)
    validate_trip_name_length(trip_in.name)
    validate_trip_description_length(trip_in.description)
    
    # Validar duplicados
    if get_trip_by_start_date_and_user(db, trip_in.start_date, trip_in.user_id):
        raise AppError(400, "TRIP_ALREADY_EXISTS", "El viaje ya existe")
    
    # Crear trip después de todas las validaciones
    trip = Trip(**trip_in.model_dump())
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip

def update(db: Session, trip_id: int, trip_in: TripUpdate) -> Trip:
    # Reutilizar get_trip_by_id
    trip = get_trip_by_id(db, trip_id)
    if not trip:
        raise AppError(404, "TRIP_NOT_FOUND", "El viaje no existe")
    
    # Convertir a dict solo con campos no-None
    trip_data = trip_in.model_dump(exclude_unset=True)
    
    # Validar fechas si se están actualizando (considerar valores actuales si no se envían)
    start_date = trip_data.get('start_date', trip.start_date)
    end_date = trip_data.get('end_date', trip.end_date)
    validate_trip_dates(start_date, end_date)
    
    # Validar longitud de name si se está actualizando
    if 'name' in trip_data and trip_data['name'] is not None:
        validate_trip_name_length(trip_data['name'])
    
    # Validar longitud de description si se está actualizando
    if 'description' in trip_data and trip_data['description'] is not None:
        validate_trip_description_length(trip_data['description'])
    
    # Actualizar solo campos no-None
    for key, value in trip_data.items():
        if value is not None:
            setattr(trip, key, value)
    
    db.commit()
    db.refresh(trip)
    return trip

def delete(db: Session, *, id: int) -> None:
    # Reutilizar get_trip_by_id
    trip = get_trip_by_id(db, id)
    if not trip:
        raise AppError(404, "TRIP_NOT_FOUND", "El viaje no existe")
    
    db.delete(trip)
    db.commit()

