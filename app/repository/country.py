from sqlalchemy.orm import Session
from app.db.models.country import Country
from typing import List, Optional

class CountryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: Optional[int] = 100) -> List[Country]:
        query = self.db.query(Country).offset(skip)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def get_by_id(self, country_id: int) -> Optional[Country]:
        return self.db.query(Country).filter(Country.id == country_id).first()

    def get_by_name(self, name: str) -> Optional[Country]:
        return self.db.query(Country).filter(Country.name == name).first()
    
    def get_by_code_alpha2(self, code: str) -> Optional[Country]:
        """Buscar país por código ISO 3166-1 alpha-2"""
        if not code:
            return None
        return self.db.query(Country).filter(Country.code_alpha2 == code.upper()).first()
    
    def get_by_code_alpha3(self, code: str) -> Optional[Country]:
        """Buscar país por código ISO 3166-1 alpha-3"""
        if not code:
            return None
        return self.db.query(Country).filter(Country.code_alpha3 == code.upper()).first()

    def create(self, country: Country) -> Country:
        # Nota: No hacemos commit aquí, lo maneja el servicio con el decorador @transactional
        self.db.add(country)
        return country
        
    def bulk_create(self, countries: List[Country]) -> List[Country]:
        """Inserción masiva de países para mejor rendimiento"""
        self.db.add_all(countries)
        return countries

    def update(self, country: Country, country_data: dict) -> Country:
        for key, value in country_data.items():
            if value is not None:
                setattr(country, key, value)
        return country

    def delete(self, country: Country) -> None:
        self.db.delete(country)
