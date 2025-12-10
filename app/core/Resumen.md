# 📚 Resumen - Carpeta `app/core/`

## 📋 ¿Qué es este módulo?

La carpeta `app/core/` contiene **configuración central y utilidades** que son usadas por toda la aplicación. Es el "núcleo" que proporciona:

- ⚙️ Configuración desde variables de entorno
- 🚨 Manejo centralizado de excepciones
- 🔧 Decoradores reutilizables
- 📋 Constantes y códigos de error

## 🎯 Responsabilidad

Este módulo es responsable de:

- ✅ Leer variables de entorno del archivo `.env`
- ✅ Validar configuración (SECRET_KEY, DATABASE_URL, etc.)
- ✅ Definir excepciones personalizadas
- ✅ Formatear respuestas de error consistentes
- ✅ Proporcionar decoradores útiles (`@transactional`)
- ✅ Centralizar constantes y códigos de error

## 📁 Estructura de Archivos

```
core/
├── config.py       # Configuración desde .env (Settings)
├── constants.py    # Constantes y códigos de error (ErrorCode)
├── decorators.py   # Decoradores (@transactional)
└── exceptions.py   # Excepciones y manejadores de error
```

## 🛠️ Tecnologías Usadas

| Tecnología        | Propósito                                |
| ----------------- | ---------------------------------------- |
| **python-dotenv** | Cargar variables de entorno desde `.env` |
| **os**            | Leer variables de entorno                |
| **functools**     | Decoradores (@wraps)                     |

## 📄 Archivos Principales

### 1️⃣ `config.py` - Configuración

**Propósito:** Centralizar toda la configuración de la aplicación en una clase `Settings`.

```python
import os
from dotenv import load_dotenv

load_dotenv()  # Carga .env

class Settings:
    """Configuración desde variables de entorno"""

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fallback-key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    # Database
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "aurevia")

    @property
    def database_url(self) -> str:
        """Construye la URL de conexión"""
        return f"mysql+mysqlconnector://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"

    # CORS
    @property
    def allowed_origins(self) -> list[str]:
        """Lista de orígenes permitidos para CORS"""
        origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8100")
        return [o.strip() for o in origins.split(",")]

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

settings = Settings()  # Instancia global
```

**Uso:**

```python
from app.core.config import settings

# Acceder a configuración
print(settings.database_url)  # mysql+mysqlconnector://root:...
print(settings.SECRET_KEY)     # tu-clave-secreta
print(settings.allowed_origins) # ['http://localhost:8100']
```

**📝 Archivo .env:**

```env
# Database
MYSQL_USER=root
MYSQL_PASSWORD=mipassword
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=aurevia

# JWT
SECRET_KEY=clave-super-secreta-de-al-menos-32-caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
ALLOWED_ORIGINS=http://localhost:8100,http://127.0.0.1:8100

# App
ENVIRONMENT=development
DEBUG=True
```

---

### 2️⃣ `constants.py` - Constantes

**Propósito:** Definir códigos de error y mensajes constantes.

```python
class ErrorCode:
    """Códigos de error de la aplicación"""

    # Errores de Usuario
    USER_NOT_FOUND = "USER_NOT_FOUND"
    EMAIL_DUPLICATED = "EMAIL_DUPLICATED"
    USERNAME_DUPLICATED = "USERNAME_DUPLICATED"
    INVALID_PASSWORD = "INVALID_PASSWORD"
    EMAIL_NOT_FOUND = "EMAIL_NOT_FOUND"

    # Errores de Viaje
    TRIP_NOT_FOUND = "TRIP_NOT_FOUND"
    INVALID_DATES = "INVALID_DATES"

    # Errores de País/Ciudad
    COUNTRY_NOT_FOUND = "COUNTRY_NOT_FOUND"
    CITY_NOT_FOUND = "CITY_NOT_FOUND"

    # Errores de Comentario
    COMMENT_NOT_FOUND = "COMMENT_NOT_FOUND"

    # Errores Generales
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
```

**Uso:**

```python
from app.core.constants import ErrorCode

# En vez de strings hardcodeadas
raise AppError(404, "USER_NOT_FOUND", "Usuario no existe")

# Mejor con constantes
raise AppError(404, ErrorCode.USER_NOT_FOUND, "Usuario no existe")
```

**Ventajas:**

- ✅ Evita typos (autocompletado del IDE)
- ✅ Fácil de refactorizar
- ✅ Documentación clara de todos los códigos

---

### 3️⃣ `decorators.py` - Decoradores

**Propósito:** Decoradores reutilizables para funciones de servicio.

#### Decorador `@transactional`

Maneja transacciones de base de datos automáticamente:

```python
from functools import wraps
from sqlalchemy.orm import Session

def transactional(func):
    """
    Decorador para manejar transacciones automáticamente.

    - Si la función termina bien → COMMIT
    - Si hay excepción → ROLLBACK
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        # 1. Busca db en args, kwargs o self.db
        db = get_db_session(*args, **kwargs)

        if not db:
            return await func(*args, **kwargs)

        try:
            result = await func(*args, **kwargs)
            db.commit()
            if hasattr(result, "__dict__"):
                db.refresh(result)
            return result
        except AppError:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise AppError(500, ErrorCode.INTERNAL_SERVER_ERROR, str(e))

    # Soporte para funciones síncronas y asíncronas
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
```

**Características:**

- ✅ Soporta funciones **síncronas** y **asíncronas** (`async def`).
- ✅ Busca la sesión de BD en:
  1. Argumentos posicionales (si alguno es `Session`).
  2. Argumentos nombrados (`kwargs['db']`).
  3. Atributo `self.db` (útil para métodos de clase Service).

**Uso:**

```python
class UserService:
    @transactional
    def create(self, email, username, password):
        # Si algo falla aquí, rollback automático
        user = User(email=email, username=username, ...)
        self.repo.create(user)
        # Commit automático al terminar
        return user
```

**Sin decorador (tedioso):**

```python
def create(self, email, username, password):
    try:
        user = User(...)
        self.repo.create(user)
        self.db.commit()  # Manual
        self.db.refresh(user)  # Manual
        return user
    except Exception:
        self.db.rollback()  # Manual
        raise
```

---

### 4️⃣ `exceptions.py` - Excepciones

**Propósito:** Definir excepciones personalizadas y sus manejadores.

#### Clase `AppError`

```python
class AppError(Exception):
    """Excepción personalizada de la aplicación"""

    def __init__(self, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(self.message)
```

**Uso:**

```python
# Lanzar error personalizado
if not user:
    raise AppError(404, ErrorCode.USER_NOT_FOUND, "El usuario no existe")

# En vez de HTTPException de FastAPI
# raise HTTPException(status_code=404, detail="Usuario no existe")
```

#### Manejadores de Excepciones

Convierten excepciones en respuestas JSON consistentes:

```python
async def app_error_handler(request: Request, exc: AppError):
    """Maneja AppError personalizados"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "type": "app_error"
            },
            "path": str(request.url.path)
        }
    )

async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Maneja errores de validación de Pydantic"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Error de validación de datos",
                "type": "validation_error"
            },
            "details": errors,
            "path": str(request.url.path)
        }
    )
```

**Registro en main.py:**

```python
from app.core.exceptions import (
    AppError, app_error_handler,
    validation_error_handler,
    ...
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
# ...
```

#### Formato de Respuesta de Error

Todos los errores siguen el mismo formato JSON:

```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "El usuario no existe",
    "type": "app_error"
  },
  "details": {
    "user_id": 999
  },
  "path": "/api/v1/auth/id/999"
}
```

**Beneficios:**

- ✅ Respuestas consistentes
- ✅ Fácil de parsear en el cliente
- ✅ Información útil para debugging (path, details)

## 💡 Conceptos Clave

### 1. **Configuración por Entorno**

Diferentes `.env` para cada entorno:

```
.env.development  → Desarrollo local
.env.staging      → Servidor de pruebas
.env.production   → Producción

# Cargar según entorno
load_dotenv(f".env.{ENVIRONMENT}")
```

### 2. **Fail-Fast Configuration**

Si falta configuración crítica, fallar al inicio:

```python
class Settings:
    def __post_init__(self):
        if self.ENVIRONMENT == "production" and self.SECRET_KEY == "fallback-key":
            raise ValueError("SECRET_KEY must be set in production!")
```

### 3. **Manejo Centralizado de Errores**

En vez de:

```python
# ❌ Cada endpoint maneja errores diferente
try:
    ...
except Exception as e:
    return {"error": str(e)}  # Formato inconsistente
```

Mejor:

```python
# ✅ Lanzar AppError, el manejador formatea automáticamente
raise AppError(404, ErrorCode.USER_NOT_FOUND, "Usuario no existe")
# → Respuesta JSON consistente automática
```

### 4. **Decoradores para Cross-Cutting Concerns**

Separar lógica transversal (transacciones, logging, cache):

```python
@transactional   # Maneja commit/rollback
@log_execution   # Log entrada/salida
@cache_result    # Cachea resultado
def expensive_operation():
    ...
```

## 🔗 Relación con Otros Módulos

```
┌──────────────┐
│    main.py   │  ← Lee settings, registra manejadores de error
└──────┬───────┘
       │
       ↓
┌──────────────┐
│    core/     │  ← ESTÁS AQUÍ
│  config.py   │    Proporciona configuración
│  exceptions.py│   Maneja errores
│  decorators.py│   Proporciona @transactional
└──────┬───────┘
       │
       ↓
┌──────────────┐
│  Todos los   │  ← Usan settings, AppError, @transactional
│   módulos    │
└──────────────┘
```

## 📖 Para Aprender Más

1. Lee `config.py` para ver configuración completa
2. Revisa `exceptions.py` para tipos de error
3. Prueba lanzar `AppError` en un endpoint
4. Investiga patrón Configuration Object

**Siguiente paso:** Lee [`../db/Resumen.md`](../db/Resumen.md) para la capa de datos.
