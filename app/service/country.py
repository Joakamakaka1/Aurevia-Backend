from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models.country import Country
from app.schemas.country import CountryCreate, CountryUpdate
from app.core.exceptions import AppError
from app.core.constants import ErrorCode
from app.core.decorators import transactional
from app.repository.country import CountryRepository

class CountryService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CountryRepository(db)

    def get_all(self) -> List[Country]:
        return self.repo.get_all()

    def get_by_id(self, country_id: int) -> Optional[Country]:
        return self.repo.get_by_id(country_id)

    def get_by_name(self, name: str) -> Optional[Country]:
        return self.repo.get_by_name(name)

    @transactional
    def create(self, country_in: CountryCreate) -> Country:
        # Validar nombre duplicado
        if self.repo.get_by_name(country_in.name):
            raise AppError(409, ErrorCode.COUNTRY_ALREADY_EXISTS, "El país ya existe")
        
        country = Country(name=country_in.name)
        return self.repo.create(country)

    @transactional
    def update(self, country_id: int, country_in: CountryUpdate) -> Country:
        country = self.repo.get_by_id(country_id)
        if not country: 
            raise AppError(404, ErrorCode.COUNTRY_NOT_FOUND, "El país no existe")
        
        # Convertir a dict solo con campos no-None
        country_data = country_in.model_dump(exclude_unset=True)
        
        # Validar nombre duplicado si se está actualizando (excluyendo el mismo país)
        if 'name' in country_data and country_data['name'] is not None:
            existing_country = self.repo.get_by_name(country_data['name'])
            if existing_country and existing_country.id != country_id:
                raise AppError(409, ErrorCode.COUNTRY_ALREADY_EXISTS, "El país ya existe")
            
        return self.repo.update(country, country_data)

    @transactional
    def delete(self, country_id: int) -> None:
        country = self.repo.get_by_id(country_id)
        if not country:
            raise AppError(404, ErrorCode.COUNTRY_NOT_FOUND, "El país no existe")
        
        self.repo.delete(country)
