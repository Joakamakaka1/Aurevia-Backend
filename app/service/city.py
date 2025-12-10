from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from app.db.models.city import City
from app.schemas.city import CityCreate, CityUpdate
from app.core.exceptions import AppError
from app.core.constants import ErrorCode
from app.core.decorators import transactional
from app.repository.city import CityRepository
from app.repository.country import CountryRepository
from app.service.external_api import ExternalAPIService
import logging
import time

logger = logging.getLogger(__name__)

class CityService:

    '''
    Servicio de ciudades. 
    
    Responsabilidades:
    - Valida duplicados de nombre.
    - Poblar ciudades desde API externa.
    '''
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = CityRepository(db)

    def get_all(self) -> List[City]:
        return self.repo.get_all()

    def get_by_name(self, name: str) -> Optional[City]:
        return self.repo.get_by_name(name)

    def get_by_id(self, city_id: int) -> Optional[City]:
        return self.repo.get_by_id(city_id)
        
    def get_by_country_code(self, country_code: str) -> List[City]:
        return self.repo.get_by_country_code(country_code)

    @transactional
    def create(self, city_in: CityCreate) -> City:
        # Validar nombre duplicado en el mismo país
        # Nota: La lógica original validaba solo nombre, lo cual es muy restrictivo globalmente
        # pero mantenemos la compatibilidad
        existing_city = self.repo.get_by_name(city_in.name)
        if existing_city:
             # Si existe, verificamos si es del mismo país para lanzar error
             if existing_city.country_id == city_in.country_id:
                 raise AppError(409, ErrorCode.CITY_ALREADY_EXISTS, "La ciudad ya existe en este país")
        
        city = City(**city_in.model_dump())
        return self.repo.create(city)
        
    @transactional
    async def populate_from_api(
        self, 
        country_code: str, 
        limit: int = 100,
        min_population: int = 10000
    ) -> Dict[str, int]:
        """
        Pobla la tabla de ciudades desde GeoNames API para un país específico.
        """
        stats = {"created": 0, "updated": 0, "errors": 0}
        
        try:
            # Verificar que el país existe en la base de datos
            country_repo = CountryRepository(self.db)
            country = country_repo.get_by_code_alpha2(country_code.upper())
            
            if not country:
                # Intentar buscar por alpha3 si falla alpha2
                country = country_repo.get_by_code_alpha3(country_code.upper())
            
            if not country:
                raise AppError(
                    404, 
                    ErrorCode.COUNTRY_NOT_FOUND, 
                    f"País con código {country_code} no encontrado en la base de datos. Poble los países primero."
                )
            
            # Obtener datos de la API externa
            external_api = ExternalAPIService()
            # Usar siempre alpha2 para GeoNames
            api_code = country.code_alpha2 if country.code_alpha2 else country_code 
            
            cities_data = await external_api.fetch_cities_by_country(
                api_code, 
                max_rows=limit,
                min_population=min_population
            )
            
            logger.info(f"Obtenidas {len(cities_data)} ciudades de GeoNames API para {country_code}")
            
            # OPTIMIZACIÓN: Cargar todas las ciudades existentes del país en memoria
            # Esto evita hacer una query SELECT por cada ciudad (N+1 problema)
            existing_cities = self.repo.get_by_country_id(country.id)
            
            # Crear diccionarios para búsqueda rápida O(1)
            existing_by_geoname = {c.geoname_id: c for c in existing_cities if c.geoname_id}
            existing_by_name = {c.name: c for c in existing_cities}
            
            for city_data in cities_data:
                try:
                    # Añadir country_id a los datos
                    city_data["country_id"] = country.id
                    
                    # Verificar existencia en memoria
                    existing_city = None
                    
                    # 1. Por GeoName ID
                    if city_data.get("geoname_id"):
                        existing_city = existing_by_geoname.get(city_data["geoname_id"])
                    
                    # 2. Fallback: Por nombre (si no se encontró por ID)
                    if not existing_city:
                        existing_city = existing_by_name.get(city_data["name"])
                    
                    if existing_city:
                        # Actualizar ciudad existente
                        self.repo.update(existing_city, city_data)
                        stats["updated"] += 1
                    else:
                        # Crear nueva ciudad
                        new_city = City(**city_data)
                        self.repo.create(new_city)
                        # Actualizar índices en memoria por si hay duplicados en el mismo batch de la API
                        if new_city.geoname_id:
                            existing_by_geoname[new_city.geoname_id] = new_city
                        existing_by_name[new_city.name] = new_city
                        
                        stats["created"] += 1
                        
                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"Error procesando ciudad {city_data.get('name', 'unknown')}: {str(e)}")
            
            logger.info(f"Población de ciudades para {country_code} completada: {stats}")
            return stats
            
        except AppError:
            raise
        except Exception as e:
            logger.error(f"Error fatal al poblar ciudades de {country_code}: {str(e)}")
            raise AppError(500, ErrorCode.INTERNAL_SERVER_ERROR, f"Error al poblar ciudades: {str(e)}")

    @transactional
    async def populate_all_countries_cities(
        self, 
        limit_per_country: int = 50,
        min_population: int = 50000
    ) -> Dict[str, any]:
        """
        Pobla ciudades para todos los países en la base de datos.
        """
        total_stats = {
            "created": 0, 
            "updated": 0, 
            "errors": 0,
            "countries_processed": 0,
            "countries_failed": 0
        }
        
        # Obtener todos los países
        country_repo = CountryRepository(self.db)
        countries = country_repo.get_all()
        
        logger.info(f"Iniciando población masiva de ciudades para {len(countries)} países")
        
        for country in countries:
            if not country.code_alpha2:
                continue
            
            try:
                # Poblar ciudades para este país
                # Reducimos el logging para no saturar
                stats = await self.populate_from_api(
                    country.code_alpha2,
                    limit=limit_per_country,
                    min_population=min_population
                )
                
                total_stats["created"] += stats["created"]
                total_stats["updated"] += stats["updated"]
                total_stats["errors"] += stats["errors"]
                total_stats["countries_processed"] += 1
                
            except Exception as e:
                logger.error(f"Error procesando país {country.name}: {str(e)}")
                total_stats["countries_failed"] += 1
        
        return total_stats

    @transactional
    def update(self, city_id: int, city_in: CityUpdate) -> City:
        city = self.repo.get_by_id(city_id)
        if not city:
            raise AppError(404, ErrorCode.CITY_NOT_FOUND, "La ciudad no existe")
        
        # Convertir a dict solo con campos no-None
        city_data = city_in.model_dump(exclude_unset=True)
        
        # Validar nombre duplicado si se está actualizando
        if 'name' in city_data and city_data['name'] is not None:
             # Verificar duplicado solo en el MISMO país
             target_country_id = city_data.get('country_id', city.country_id)
             
             existing_city = self.db.query(City).filter(
                 City.name == city_data['name'],
                 City.country_id == target_country_id
             ).first()
             
             if existing_city and existing_city.id != city_id:
                  raise AppError(409, ErrorCode.CITY_ALREADY_EXISTS, "La ciudad ya existe en este país")
            
        return self.repo.update(city, city_data)

    @transactional
    def delete(self, city_id: int) -> None:
        city = self.repo.get_by_id(city_id)
        if not city:
            raise AppError(404, ErrorCode.CITY_NOT_FOUND, "La ciudad no existe")
        
        self.repo.delete(city)
