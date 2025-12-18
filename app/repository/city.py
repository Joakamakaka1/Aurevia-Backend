from sqlalchemy.orm import Session
from app.db.models.city import City
from app.db.models.country import Country
from typing import List, Optional

class CityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: Optional[int] = 100) -> List[City]:
        query = self.db.query(City).offset(skip)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def get_by_id(self, city_id: int) -> Optional[City]:
        return self.db.query(City).filter(City.id == city_id).first()

    def get_by_name(self, name: str) -> Optional[City]:
        # Nota: Buscar solo por nombre puede ser ambiguo (ej: 'San José' existe en muchos países)
        return self.db.query(City).filter(City.name == name).first()
    
    def get_by_name_and_country(self, name: str, country_id: int) -> Optional[City]:
        """Buscar ciudad por nombre y país (composite unique)"""
        return self.db.query(City).filter(
            City.name == name,
            City.country_id == country_id
        ).first()
        
    def get_by_geoname_id(self, geoname_id: int) -> Optional[City]:
        """Buscar ciudad por ID de GeoNames"""
        if not geoname_id:
            return None
        return self.db.query(City).filter(City.geoname_id == geoname_id).first()
    
    def get_by_country_id(self, country_id: int) -> List[City]:
        """Obtener todas las ciudades de un país"""
        return self.db.query(City).filter(City.country_id == country_id).all()

    def get_by_country_code(self, country_code: str) -> List[City]:
        """Obtener todas las ciudades filtrando por código de país (ISO Alpha-2 o Alpha-3)"""
        code = country_code.upper()
        return (
            self.db.query(City)
            .join(Country)
            .filter(
                (Country.code_alpha2 == code) | (Country.code_alpha3 == code)
            )
            .all()
        )

    def create(self, city: City) -> City:
        # Nota: No hacemos commit aquí, lo maneja el servicio con el decorador @transactional
        self.db.add(city)
        return city
        
    def bulk_create(self, cities: List[City]) -> List[City]:
        """Inserción masiva de ciudades para mejor rendimiento"""
        self.db.add_all(cities)
        return cities

    def update(self, city: City, city_data: dict) -> City:
        for key, value in city_data.items():
            if value is not None:
                setattr(city, key, value)
        return city

    def delete(self, city: City) -> None:
        self.db.delete(city)
