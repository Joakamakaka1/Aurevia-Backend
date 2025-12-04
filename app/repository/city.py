from sqlalchemy.orm import Session
from app.db.models.city import City
from typing import List, Optional

class CityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[City]:
        return self.db.query(City).all()

    def get_by_id(self, city_id: int) -> Optional[City]:
        return self.db.query(City).filter(City.id == city_id).first()

    def get_by_name(self, name: str) -> Optional[City]:
        return self.db.query(City).filter(City.name == name).first()

    def create(self, city: City) -> City:
        # Nota: No hacemos commit aquí, lo maneja el servicio con el decorador @transactional
        self.db.add(city)
        return city

    def update(self, city: City, city_data: dict) -> City:
        for key, value in city_data.items():
            if value is not None:
                setattr(city, key, value)
        return city

    def delete(self, city: City) -> None:
        self.db.delete(city)
