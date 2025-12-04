from sqlalchemy.orm import Session
from app.db.models.city import City
from app.core.exceptions import AppError
from app.schemas.city import CityCreate, CityUpdate


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

# Metodo auxiliar
def validate_city_name_length(name: str) -> None:
    """Valida longitud del nombre de la ciudad"""
    if len(name) < 2:
        raise AppError(400, "NAME_TOO_SHORT", "El nombre de la ciudad debe tener al menos 2 caracteres")
    if len(name) > 100:
        raise AppError(400, "NAME_TOO_LONG", "El nombre de la ciudad no puede tener más de 100 caracteres")


def create_city(db: Session, city_in: CityCreate) -> City:
    """
    
    ** Crear una nueva ciudad **

    - Asignamos los atributos indicados por parámetro a city y la añadimos a la base de datos.

    """
    try:
        # Validar nombre duplicado
        if get_city_by_name(db, city_in.name):
            raise AppError(409, "CITY_ALREADY_EXISTS", "La ciudad ya existe")
        
        # Validar longitud del nombre (también validado en schema, pero mantenemos por si acaso)
        validate_city_name_length(city_in.name)

        city = City(**city_in.model_dump())

        db.add(city)
        db.commit()
        db.refresh(city)
        return city

    except Exception as e:
        db.rollback()
        raise AppError(500, "INTERNAL_SERVER_ERROR", str(e))

def update_city(db: Session, city_id: int, city_in: CityUpdate) -> City:
    # Reutilizar get_city_by_id
    try:
        city = get_city_by_id(db, city_id)
        if not city:
            raise AppError(404, "CITY_NOT_FOUND", "La ciudad no existe")
        
        # Convertir a dict solo con campos no-None
        city_data = city_in.model_dump(exclude_unset=True)
        
        # Validar nombre duplicado si se está actualizando (excluyendo la misma ciudad)
        if 'name' in city_data and city_data['name'] is not None:
            existing_city = get_city_by_name(db, city_data['name'])
            if existing_city and existing_city.id != city_id:
                raise AppError(409, "CITY_ALREADY_EXISTS", "La ciudad ya existe")
            
            # Validar longitud del nombre
            validate_city_name_length(city_data['name'])
        
        # Actualizar solo campos no-None
        for key, value in city_data.items():
            if value is not None:
                setattr(city, key, value)

        db.commit()
        db.refresh(city)
        return city

    except Exception as e:
        db.rollback()
        raise AppError(500, "INTERNAL_SERVER_ERROR", str(e))


def delete_city(db: Session, city_id: int) -> None:
    # Reutilizar get_city_by_id
    try:
        city = get_city_by_id(db, city_id)
        if not city:
            raise AppError(404, "CITY_NOT_FOUND", "La ciudad no existe")
        
        db.delete(city)
        db.commit()
        return None

    except Exception as e:
        db.rollback()
        raise AppError(500, "INTERNAL_SERVER_ERROR", str(e))



