from sqlalchemy.orm import Session
from app.db.models.trip import Trip
from app.auth.security import verify_password
from app.core.exceptions import AppError

def get_all_trips(db: Session) -> list[Trip]:
    return db.query(Trip).all()

def get_trip_by_name(db: Session, name: str) -> Trip | None:
    """

    ** Obtener un viaje por nombre **

    - Filtramos la tabla de Trip por el nombre del viaje
    - Igualamos al nombre que recibimos como parametro a la fecha encontrada.
    
    """
    return db.query(Trip).filter(Trip.name == name).first()

def get_trip_by_start_date(db: Session, strart_date: str) -> Trip | None:
    """

    ** Obtener un viaje por fecha **

    - Filtramos la tabla de Trip por la fecha del viaje
    - Igualamos la fecha que recibimos como parametro a la fecha encontrada.
    - Usamos este metodo para verificar que la fecha del viaje no se repite, para no encontrar viajes con fechas de entrada duplicados
    
    """
    return db.query(Trip).filter(Trip.start_date == strart_date).first()

# TODO: Revisar si puede coger la entidad completa y no atributo por atributo
def create (db: Session, *, name: str, description: str, start_date: str, end_date: str) -> Trip:
    " Verificamos si la fecha de entrada es posterior a la de salida "
    if(start_date > end_date):
        raise AppError(400, "INVALID_DATE", "La fecha de inicio no puede ser posterior a la fecha de fin")
        
    " Verificamos si el viaje ya existe con el metodo get_trip_by_start_date "
    if(get_trip_by_start_date(db, start_date)):
        raise AppError(400, "TRIP_ALREADY_EXISTS", "El viaje ya existe")
    
    trip = Trip(name=name, description=description, start_date=start_date, end_date=end_date)
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip

def update (db: Session, *, name: str, description: str, start_date: str, end_date: str) -> Trip:
    trip = Trip(name=name, description=description, start_date=start_date, end_date=end_date)
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip

def delete (db: Session, *, name: str, description: str, start_date: str, end_date: str) -> Trip:
    trip = Trip(name=name, description=description, start_date=start_date, end_date=end_date)
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip
