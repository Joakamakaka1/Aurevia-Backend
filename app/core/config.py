'''
Configuración de la aplicación Aurevia API

Este módulo centraliza todas las configuraciones de la aplicación,
cargadas desde variables de entorno (.env file).

Incluye:
- Configuración de JWT (SECRET_KEY, algoritmo, expiración)
- Configuración de base de datos MySQL
- Configuración de CORS
- Variables de entorno (DEBUG, ENVIRONMENT)
'''

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Settings:
    """Configuración de la aplicación desde variables de entorno"""
    
    # Application Settings (needed first for validation)
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    
    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fallback-secret-key-only-for-development")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    
    def __post_init__(self):
        """Validar configuración después de inicialización"""
        # SEGURIDAD: No permitir SECRET_KEY por defecto en producción
        if self.ENVIRONMENT != "development" and self.SECRET_KEY == "fallback-secret-key-only-for-development":
            raise ValueError(
                "SECRET_KEY must be set in production environment. "
                "Generate a secure key with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
    
    # Database
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "aurevia")
    
    @property
    def database_url(self) -> str:
        '''
        Construye la URL de conexión a MySQL dinámicamente.
        Formato: mysql+mysqlconnector://usuario:password@host:puerto/database
        '''
        return f"mysql+mysqlconnector://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
    
    # CORS
    @property
    def allowed_origins(self) -> list[str]:
        '''
        Parsea los orígenes permitidos para CORS desde variable de entorno.
        Formato en .env: "http://localhost:8100,http://127.0.0.1:8100"
        Retorna una lista de URLs permitidas.
        '''
        origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8100,http://127.0.0.1:8100")
        return [origin.strip() for origin in origins.split(",")]
    
    # External APIs
    REST_COUNTRIES_URL: str = os.getenv("REST_COUNTRIES_URL", "https://restcountries.com/v3.1")
    GEONAMES_URL: str = os.getenv("GEONAMES_URL", "http://api.geonames.org")
    GEONAMES_USERNAME: str = os.getenv("GEONAMES_USERNAME", "")

    # Application Settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

settings = Settings()
