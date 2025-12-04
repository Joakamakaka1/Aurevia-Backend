from sqlalchemy.orm import Session
from app.db.models.city import City
from app.schemas.city import CityCreate, CityUpdate
from app.core.exceptions import AppError
from app.core.constants import ErrorCode
from app.core.decorators import transactional
from app.repository.city import CityRepository

def get_all_cities(db: Session) -> list[City]:
    repo = CityRepository(db)
    return repo.get_all()

def get_city_by_name(db: Session, name: str) -> City | None:
    repo = CityRepository(db)
    return repo.get_by_name(name)

def get_city_by_id(db: Session, city_id: int) -> City | None:
    repo = CityRepository(db)
    return repo.get_by_id(city_id)

@transactional
def create_city(db: Session, city_in: CityCreate) -> City:
    repo = CityRepository(db)
    
    # Validar nombre duplicado
    if repo.get_by_name(city_in.name):
        raise AppError(409, ErrorCode.CITY_ALREADY_EXISTS, "La ciudad ya existe")
    
    # Nota: Validaciones de longitud ya las hace Pydantic

    city = City(**city_in.model_dump())
    return repo.create(city)

@transactional
def update_city(db: Session, city_id: int, city_in: CityUpdate) -> City:
    repo = CityRepository(db)
    city = repo.get_by_id(city_id)
    if not city:
        raise AppError(404, ErrorCode.CITY_NOT_FOUND, "La ciudad no existe")
    
    # Convertir a dict solo con campos no-None
    city_data = city_in.model_dump(exclude_unset=True)
    
    # Validar nombre duplicado si se está actualizando (excluyendo la misma ciudad)
    if 'name' in city_data and city_data['name'] is not None:
        existing_city = repo.get_by_name(city_data['name'])
        if existing_city and existing_city.id != city_id:
            raise AppError(409, ErrorCode.CITY_ALREADY_EXISTS, "La ciudad ya existe")
        
    return repo.update(city, city_data)

@transactional
def delete_city(db: Session, city_id: int) -> None:
    repo = CityRepository(db)
    city = repo.get_by_id(city_id)
    if not city:
        raise AppError(404, ErrorCode.CITY_NOT_FOUND, "La ciudad no existe")
    
    repo.delete(city)
