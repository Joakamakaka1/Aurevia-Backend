from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from app.db.models.country import Country
from app.schemas.country import CountryCreate, CountryUpdate
from app.core.exceptions import AppError
from app.core.constants import ErrorCode
from app.core.decorators import transactional
from app.repository.country import CountryRepository
from app.service.external_api import ExternalAPIService
import logging

logger = logging.getLogger(__name__)

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
            
        # Validar código alpha2 duplicado
        if country_in.code_alpha2 and self.repo.get_by_code_alpha2(country_in.code_alpha2):
            raise AppError(409, ErrorCode.COUNTRY_ALREADY_EXISTS, f"El código alpha-2 {country_in.code_alpha2} ya existe")

        # Validar código alpha3 duplicado
        if country_in.code_alpha3 and self.repo.get_by_code_alpha3(country_in.code_alpha3):
             raise AppError(409, ErrorCode.COUNTRY_ALREADY_EXISTS, f"El código alpha-3 {country_in.code_alpha3} ya existe")
        
        country = Country(**country_in.model_dump())
        return self.repo.create(country)
        
    @transactional
    async def populate_from_api(self) -> Dict[str, int]:
        """
        Pobla la tabla de países desde REST Countries API.
        
        Returns:
            Diccionario con estadísticas: {"created": int, "updated": int, "errors": int}
        """
        stats = {"created": 0, "updated": 0, "errors": 0}
        
        try:
            # Obtener datos de la API externa
            external_api = ExternalAPIService()
            countries_data = await external_api.fetch_all_countries()
            
            logger.info(f"Obtenidos {len(countries_data)} países de REST Countries API")
            
            for country_data in countries_data:
                try:
                    # Verificar si el país ya existe por código alpha-2 o alpha-3
                    existing_country = None
                    if country_data.get("code_alpha2"):
                        existing_country = self.repo.get_by_code_alpha2(country_data["code_alpha2"])
                    
                    if not existing_country and country_data.get("code_alpha3"):
                        existing_country = self.repo.get_by_code_alpha3(country_data["code_alpha3"])
                    
                    if not existing_country:
                        existing_country = self.repo.get_by_name(country_data["name"])
                    
                    if existing_country:
                        # Actualizar país existente
                        self.repo.update(existing_country, country_data)
                        stats["updated"] += 1
                    else:
                        # Crear nuevo país
                        new_country = Country(**country_data)
                        self.repo.create(new_country)
                        stats["created"] += 1
                        
                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"Error procesando país {country_data.get('name', 'unknown')}: {str(e)}")
            
            logger.info(f"Población de países completada: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error fatal al poblar países: {str(e)}")
            raise AppError(500, ErrorCode.INTERNAL_SERVER_ERROR, f"Error al poblar países: {str(e)}")

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
                
        # Validar código alpha2
        if 'code_alpha2' in country_data and country_data['code_alpha2']:
             existing = self.repo.get_by_code_alpha2(country_data['code_alpha2'])
             if existing and existing.id != country_id:
                 raise AppError(409, ErrorCode.COUNTRY_ALREADY_EXISTS, f"El código alpha-2 {country_data['code_alpha2']} ya existe")

        return self.repo.update(country, country_data)

    @transactional
    def delete(self, country_id: int) -> None:
        country = self.repo.get_by_id(country_id)
        if not country:
            raise AppError(404, ErrorCode.COUNTRY_NOT_FOUND, "El país no existe")
        
        self.repo.delete(country)
