from sqlalchemy.orm import Session
from app.db.models.city import City
from app.auth.security import verify_password
from app.core.exceptions import AppError
from app.schemas.city import CityCreate, CityUpdate, CityDelete


def get_all_cities(db: Session) -> list[City]:
    return db.query(City).all()


def get_city_by_name(db: Session, name: str) -> City | None:
    """
    
    ** Obtener una ciudad por su nombre **

    - Filtramos la tabla de City por nombre verificando que coincida 
    con el nombre indicado por parámetro

    """
    return db.query(City).filter(City.name == name).first()


def get_city_by_id(db: Session, city_id: int) -> City | None:
    """

    ** Obtener una ciudad por su ID **

    - Filtramos la tabla de City por ID verificando que coincida 
    con el ID indicado por parámetro

    """
    return db.query(City).filter(City.id == city_id).first()


def create_city(db: Session, city_in: CityCreate) -> City:
    """
    
    ** Crear una nueva ciudad **

    - Asignamos los atributos indicados por parámetro a city y la añadimos a la base de datos.

    """
    if get_city_by_name(db, city_in.name):
        raise AppError(409, "CITY_ALREADY_EXISTS", "La ciudad ya existe")

    city = City(**city_in.model_dump())

    db.add(city)
    db.commit()
    db.refresh(city)
    return city

def update_city(db: Session, city_id: int, city_in: CityUpdate) -> City:
    
    city = get_city_by_id(db, city_id)
    if not city:
        raise AppError(404, "CITY_NOT_FOUND", "La ciudad no existe")
    
    for key, value in city_in.model_dump().items():
        setattr(city, key, value)

    db.commit()
    db.refresh(city)
    return city


def delete_city(db: Session, city_id: int) -> None:
    city = get_city_by_id(db, city_id)

    db.delete(city)
    db.commit()
    return None



