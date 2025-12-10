import httpx
import logging
from typing import List, Dict, Any
from app.core.config import settings
from app.core.exceptions import AppError
from app.core.constants import ErrorCode

logger = logging.getLogger(__name__)

class ExternalAPIService:
    """
    Servicio para integrar con APIs externas (REST Countries y GeoNames).
    
    Responsabilidades:
    - Obtener datos de países desde REST Countries API
    - Obtener datos de ciudades desde GeoNames API
    - Manejo de errores HTTP y timeouts
    - Parseo y validación de respuestas
    """
    
    def __init__(self):
        self.rest_countries_url = settings.REST_COUNTRIES_URL
        self.geonames_url = settings.GEONAMES_URL
        self.geonames_username = settings.GEONAMES_USERNAME
        
        # Validación de configuración crítica
        if not self.geonames_username and settings.ENVIRONMENT != "test":
             logger.warning("GEONAMES_USERNAME no está configurado. Las peticiones a GeoNames fallarán.")
    
    async def fetch_all_countries(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los países desde REST Countries API.
        
        Returns:
            Lista de diccionarios con información de países normalizada
        
        Raises:
            AppError: Si hay error en la petición HTTP o al procesar datos
        """
        url = f"{self.rest_countries_url}/all"
        
        # Solo solicitamos los campos necesarios para optimizar la respuesta
        # Nota: La API v3.1 soporta filtrado por campos
        params = {"fields": "name,cca2,cca3,capital,region,subregion,population,flags"}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info(f"Fetching countries from: {url}")
                response = await client.get(url, params=params)
                
                if response.status_code != 200:
                    logger.error(f"Error fetching countries: {response.status_code} - {response.text}")
                    raise AppError(
                        502, 
                        ErrorCode.INTERNAL_SERVER_ERROR, 
                        f"Error al obtener países de REST Countries API: {response.status_code}"
                    )
                
                countries_data = response.json()
                logger.info(f"Successfully fetched {len(countries_data)} countries")
                
                return self._parse_countries(countries_data)
                
        except httpx.RequestError as e:
            logger.error(f"Connection error with REST Countries API: {str(e)}")
            raise AppError(
                503, 
                ErrorCode.INTERNAL_SERVER_ERROR, 
                f"Error de conexión con REST Countries API: {str(e)}"
            )
        except Exception as e:
            # Capturar errores de parseo o inesperados
            logger.error(f"Unexpected error in fetch_all_countries: {str(e)}")
            raise AppError(
                500,
                ErrorCode.INTERNAL_SERVER_ERROR,
                f"Error inesperado al procesar países: {str(e)}"
            )
    
    async def fetch_cities_by_country(
        self, 
        country_code: str, 
        max_rows: int = 100,
        min_population: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Obtiene ciudades de un país desde GeoNames API.
        
        Args:
            country_code: Código ISO 3166-1 alpha-2 del país (ej: "ES")
            max_rows: Número máximo de ciudades a obtener
            min_population: Población mínima para incluir la ciudad
            
        Returns:
            Lista de diccionarios con información de ciudades normalizada
        """
        if not self.geonames_username:
            raise AppError(
                500, 
                ErrorCode.INTERNAL_SERVER_ERROR, 
                "GeoNames username no configurado"
            )

        url = f"{self.geonames_url}/searchJSON"
        
        # Configuración para buscar ciudades importantes
        params = {
            "country": country_code.upper(),
            "featureClass": "P",       # P = cities, villages
            "maxRows": max_rows,
            "username": self.geonames_username,
            "orderby": "population",   # Ordenar por importancia/población
            "style": "FULL",           # Obtener todos los detalles
            "lang": "en"               # Nombres en inglés (o local)
        }
        
        # Opcional: Filtrar por tipo de ciudad para evitar aldeas muy pequeñas
        # featureCode podría usarse (PPLA, PPLC, etc) pero featureClass P + orden por población es efectivo
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info(f"Fetching cities for {country_code} from GeoNames")
                response = await client.get(url, params=params)
                
                if response.status_code != 200:
                    logger.error(f"Error fetching cities: {response.status_code} - {response.text}")
                    raise AppError(
                        502,
                        ErrorCode.INTERNAL_SERVER_ERROR,
                        f"Error al obtener ciudades de GeoNames API: {response.status_code}"
                    )
                
                data = response.json()
                
                # Verificar errores específicos de la API de GeoNames
                if "status" in data:
                    error_msg = data["status"].get("message", "Unknown error")
                    logger.error(f"GeoNames API Error: {error_msg}")
                    raise AppError(
                        502,
                        ErrorCode.INTERNAL_SERVER_ERROR,
                        f"GeoNames API Error: {error_msg}"
                    )
                
                cities_data = data.get("geonames", [])
                logger.info(f"Successfully fetched {len(cities_data)} cities for {country_code}")
                
                return self._parse_cities(cities_data, min_population)
                
        except httpx.RequestError as e:
            logger.error(f"Connection error with GeoNames API: {str(e)}")
            raise AppError(
                503,
                ErrorCode.INTERNAL_SERVER_ERROR,
                f"Error de conexión con GeoNames API: {str(e)}"
            )
    
    def _parse_countries(self, raw_data: List[Dict]) -> List[Dict]:
        """Normalize REST Countries data to our schema format"""
        parsed_countries = []
        
        for item in raw_data:
            try:
                # Extraer nombre común
                name = item.get("name", {}).get("common")
                if not name:
                    continue
                    
                # Extraer capital (lista -> string)
                capital_list = item.get("capital", [])
                capital = capital_list[0] if capital_list else None
                
                # Extraer URL de bandera (png)
                flag_url = item.get("flags", {}).get("png")
                
                parsed_countries.append({
                    "name": name,
                    "code_alpha2": item.get("cca2"),
                    "code_alpha3": item.get("cca3"),
                    "capital": capital,
                    "region": item.get("region"),
                    "subregion": item.get("subregion"),
                    "population": item.get("population"),
                    "flag_url": flag_url
                })
            except Exception as e:
                # Log error but continue processing other countries
                logger.warning(f"Error parsing country item: {str(e)}")
                continue
                
        return parsed_countries

    def _parse_cities(self, raw_data: List[Dict], min_population: int) -> List[Dict]:
        """Normalize GeoNames data to our schema format"""
        parsed_cities = []
        
        for item in raw_data:
            try:
                population = item.get("population", 0)
                
                # Filtrar ciudades que no cumplan el mínimo de población
                # (aunque la API filtre, es bueno asegurar)
                if population < min_population:
                    continue
                
                # Validar campos esenciales
                if not item.get("name") or not item.get("lat") or not item.get("lng"):
                    continue

                parsed_cities.append({
                    "name": item.get("name"),
                    "latitude": float(item.get("lat")),
                    "longitude": float(item.get("lng")),
                    "population": population,
                    "geoname_id": item.get("geonameId")
                })
            except Exception as e:
                logger.warning(f"Error parsing city item {item.get('name', 'unknown')}: {str(e)}")
                continue
                
        return parsed_cities
