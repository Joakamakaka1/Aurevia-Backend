from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models.city import City
from app.schemas.city import CityCreate, CityUpdate
from app.core.exceptions import AppError
from app.core.constants import ErrorCode
from app.core.decorators import transactional
from app.repository.city import CityRepository

class CityService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CityRepository(db)

    def get_all(self) -> List[City]:
        return self.repo.get_all()

    def get_by_name(self, name: str) -> Optional[City]:
        return self.repo.get_by_name(name)

    def get_by_id(self, city_id: int) -> Optional[City]:
        return self.repo.get_by_id(city_id)

    @transactional
    def create(self, city_in: CityCreate) -> City:
        # Validar nombre duplicado
        if self.repo.get_by_name(city_in.name):
            raise AppError(409, ErrorCode.CITY_ALREADY_EXISTS, "La ciudad ya existe")
        
        city = City(**city_in.model_dump())
        return self.repo.create(city)

    @transactional
    def update(self, city_id: int, city_in: CityUpdate) -> City:
        city = self.repo.get_by_id(city_id)
        if not city:
            raise AppError(404, ErrorCode.CITY_NOT_FOUND, "La ciudad no existe")
        
        # Convertir a dict solo con campos no-None
        city_data = city_in.model_dump(exclude_unset=True)
        
        # Validar nombre duplicado si se está actualizando (excluyendo la misma ciudad)
        if 'name' in city_data and city_data['name'] is not None:
            existing_city = self.repo.get_by_name(city_data['name'])
            if existing_city and existing_city.id != city_id:
                raise AppError(409, ErrorCode.CITY_ALREADY_EXISTS, "La ciudad ya existe")
            
        return self.repo.update(city, city_data)

    @transactional
    def delete(self, city_id: int) -> None:
        city = self.repo.get_by_id(city_id)
        if not city:
            raise AppError(404, ErrorCode.CITY_NOT_FOUND, "La ciudad no existe")
        
        self.repo.delete(city)
