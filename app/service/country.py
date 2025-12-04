from sqlalchemy.orm import Session
from app.db.models.country import Country
from app.schemas.country import CountryCreate, CountryUpdate
from app.core.exceptions import AppError
from app.core.constants import ErrorCode
from app.core.decorators import transactional
from app.repository.country import CountryRepository

def get_all_countries(db: Session) -> list[Country]:
    repo = CountryRepository(db)
    return repo.get_all()

def get_country_by_id(db: Session, country_id: int) -> Country | None:
    repo = CountryRepository(db)
    return repo.get_by_id(country_id)

def get_country_by_name(db: Session, name: str) -> Country | None:
    repo = CountryRepository(db)
    return repo.get_by_name(name)

@transactional
def create_country(db: Session, country_in: CountryCreate) -> Country:
    repo = CountryRepository(db)
    
    # Validar nombre duplicado
    if repo.get_by_name(country_in.name):
        raise AppError(409, ErrorCode.COUNTRY_ALREADY_EXISTS, "El país ya existe")
    
    # Nota: Validaciones de longitud ya las hace Pydantic
    
    country = Country(name=country_in.name)
    return repo.create(country)

@transactional
def update_country(db: Session, country_id: int, country_in: CountryUpdate) -> Country:
    repo = CountryRepository(db)
    country = repo.get_by_id(country_id)
    if not country: 
        raise AppError(404, ErrorCode.COUNTRY_NOT_FOUND, "El país no existe")
    
    # Convertir a dict solo con campos no-None
    country_data = country_in.model_dump(exclude_unset=True)
    
    # Validar nombre duplicado si se está actualizando (excluyendo el mismo país)
    if 'name' in country_data and country_data['name'] is not None:
        existing_country = repo.get_by_name(country_data['name'])
        if existing_country and existing_country.id != country_id:
            raise AppError(409, ErrorCode.COUNTRY_ALREADY_EXISTS, "El país ya existe")
        
    return repo.update(country, country_data)

@transactional
def delete_country(db: Session, country_id: int) -> None:
    repo = CountryRepository(db)
    country = repo.get_by_id(country_id)
    if not country:
        raise AppError(404, ErrorCode.COUNTRY_NOT_FOUND, "El país no existe")
    
    repo.delete(country)
