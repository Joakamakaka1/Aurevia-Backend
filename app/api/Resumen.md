# 📚 Resumen - Carpeta `app/api/`

## 📋 ¿Qué es este módulo?

La carpeta `app/api/` contiene la **capa de endpoints HTTP** (también llamada capa de presentación o controllers). Es la "puerta de entrada" de tu API donde se reciben las peticiones de los clientes.

## 🎯 Responsabilidad

Este módulo es responsable de:

- ✅ **Definir rutas HTTP** (GET, POST, PUT, DELETE)
- ✅ **Recibir peticiones** del cliente (JSON, query params, path params)
- ✅ **Validar entrada** usando Pydantic schemas
- ✅ **Delegar lógica** a la capa de servicios
- ✅ **Serializar respuestas** a JSON
- ✅ **Retornar códigos HTTP** apropiados (200, 201, 404, etc.)

**⚠️ Lo que NO hace:**

- ❌ No contiene lógica de negocio (eso va en `service/`)
- ❌ No hace queries directas a BD (eso va en `repository/`)
- ❌ No define modelos de BD (eso va en `db/models/`)

## 📁 Estructura de Archivos

```
api/
├── deps.py                    # Dependencias compartidas
└── v1/                        # Versión 1 de la API
    ├── __init__.py            # Agrupa todos los routers
    └── endpoints/             # Endpoints por entidad
        ├── city.py            # Endpoints de ciudades
        ├── comment.py         # Endpoints de comentarios
        ├── country.py         # Endpoints de países
        ├── friendship.py      # Endpoints de amistad (comentado)
        ├── healthy.py         # Health check
        ├── trip.py            # Endpoints de viajes
        └── user.py            # Endpoints de usuarios/auth
```

## 🛠️ Tecnologías Usadas

| Tecnología    | Propósito                                 |
| ------------- | ----------------------------------------- |
| **FastAPI**   | Framework web para crear endpoints        |
| **APIRouter** | Agrupar endpoints por tema                |
| **Depends()** | Inyección de dependencias                 |
| **status**    | Códigos HTTP estándar                     |
| **Pydantic**  | Validación automática de request/response |

## 🔄 Flujo de Datos

### Flujo de una Petición (Request → Response)

```
1️⃣ CLIENTE hace petición
   ↓
   POST /api/v1/auth/login
   Body: {"email": "user@mail.com", "password": "123"}

2️⃣ FASTAPI enruta a endpoints/user.py
   ↓ Encuentra el router que coincide con /v1/auth/login

3️⃣ VALIDACIÓN con Pydantic
   ↓ Valida Body con schema UserLogin
   ↓ Si es inválido → 422 Unprocessable Entity

4️⃣ INYECCIÓN de dependencias
   ↓ Depends(get_user_service) → Instancia UserService

5️⃣ DELEGAR a Service Layer
   ↓ service.authenticate(email, password)
   ↓ (Service hace toda la lógica)

6️⃣ SERIALIZAR respuesta
   ↓ Pydantic convierte objeto User → JSON con schema Token

7️⃣ RESPONDER al cliente
   ↓ 200 OK
   Body: {"access_token": "eyJ...", "user": {...}}
```

## 💡 Versionado de API (v1/)

### ¿Por qué versionar?

El versionado permite **evolucionar la API sin romper clientes existentes**:

```
/api/v1/trip/  → Versión actual (estable)
/api/v2/trip/  → Versión futura (nuevas features)
```

**Beneficios:**

- Los clientes antiguos siguen funcionando en `/v1`
- Los nuevos usan `/v2` con mejoras
- Migración gradual sin downtime

### Estructura de v1

```python
# v1/__init__.py
from fastapi import APIRouter
from app.api.v1.endpoints import user, trip, comment, ...

api_router = APIRouter()
api_router.include_router(user.router)
api_router.include_router(trip.router)
# ...
```

Este router se incluye en `main.py` con prefijo `/api`:

```python
app.include_router(api_router, prefix="/api")
# Resultado: /api/v1/auth/, /api/v1/trip/, etc.
```

## 📄 Archivos Principales

### `deps.py` - Dependencias Compartidas

Provee funciones para **inyección de dependencias** en endpoints:

```python
def get_db() -> Generator[Session, None, None]:
    """Proporciona sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Proporciona instancia de UserService"""
    return UserService(db)
```

**Uso en endpoints:**

```python
@router.post("/login")
def login(
    payload: UserLogin,
    service: UserService = Depends(get_user_service)  # ← Inyección
):
    return service.authenticate(...)
```

### `v1/__init__.py` - Router Principal

Agrupa todos los routers de endpoints:

```python
api_router = APIRouter()
api_router.include_router(user.router)      # /v1/auth/...
api_router.include_router(trip.router)      # /v1/trip/...
api_router.include_router(comment.router)   # /v1/comment/...
api_router.include_router(country.router)   # /v1/country/...
api_router.include_router(city.router)      # /v1/city/...
api_router.include_router(healthy.router)   # /v1/healthy
```

## 📝 Ejemplo Práctico: Endpoint Completo

### `endpoints/trip.py`

```python
from fastapi import APIRouter, Depends, status
from app.schemas.trip import TripCreate, TripOut
from app.service.trip import TripService
from app.api.deps import get_trip_service

router = APIRouter(prefix="/v1/trip", tags=["Trips"])

@router.post(
    "/",
    response_model=TripOut,           # Schema de salida
    status_code=status.HTTP_201_CREATED
)
def create_trip(
    payload: TripCreate,              # Schema de entrada (validación automática)
    service: TripService = Depends(get_trip_service)  # Inyección
):
    """
    Crear un nuevo viaje.

    - **name**: Nombre del viaje (3-100 chars)
    - **description**: Descripción (10-500 chars)
    - **start_date**: Fecha inicio
    - **end_date**: Fecha fin
    - **user_id**: ID del usuario
    - **country_id**: ID del país
    """
    return service.create(
        name=payload.name,
        description=payload.description,
        start_date=payload.start_date,
        end_date=payload.end_date,
        user_id=payload.user_id,
        country_id=payload.country_id
    )
```

**Desglose:**

1. `@router.post("/")` → Define ruta POST /v1/trip/
2. `response_model=TripOut` → Valida y serializa respuesta
3. `status_code=201` → Retorna 201 Created al crear
4. `payload: TripCreate` → Valida body automáticamente
5. `Depends(get_trip_service)` → Inyecta TripService
6. `return service.create(...)` → Delega al service layer

## 🌟 Características de FastAPI

### 1. Validación Automática

```python
@router.post("/")
def create_trip(payload: TripCreate):  # ← Pydantic valida automáticamente
    # Si payload es inválido, FastAPI retorna 422 automáticamente
    # No necesitas if/else manual
```

### 2. Documentación Automática

FastAPI genera docs interactivas en:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Tipado Completo

```python
def get_trip(trip_id: int) -> Trip:  # ← IDEs autocompletan
    ...
```

### 4. Dependency Injection

```python
def endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: TripService = Depends(get_trip_service)
):
    # Todas las dependencias ya instanciadas
```

## 🎨 Patrones de Diseño

### 1. **Router Pattern**

Cada entidad tiene su proprio router:

```python
user_router = APIRouter(prefix="/v1/auth", tags=["Auth"])
trip_router = APIRouter(prefix="/v1/trip", tags=["Trips"])
```

### 2. **Thin Controllers**

Los endpoints son "delgados", solo coordinan:

```python
def create_trip(payload: TripCreate, service: TripService):
    return service.create(...)  # ← Toda la lógica en service
```

### 3. **Schema-First**

Siempre validar entrada/salida con schemas:

```python
@router.post("/", response_model=TripOut)  # ← Output schema
def create(payload: TripCreate):           # ← Input schema
```

## 🔗 Relación con Otros Módulos

```
┌─────────────┐
│   CLIENTE   │
└──────┬──────┘
       │ HTTP Request
       ↓
┌──────────────────┐
│  api/endpoints/  │  ← ESTÁS AQUÍ
└──────┬───────────┘
       │ Llama a
       ↓
┌──────────────────┐
│    service/      │  (Lógica de negocio)
└──────┬───────────┘
       │
       ↓
┌──────────────────┐
│   repository/    │  (Queries SQL)
└──────┬───────────┘
       │
       ↓
┌──────────────────┐
│   db/models/     │  (ORM)
└──────────────────┘
```

## 📖 Para Aprender Más

1. Abre un endpoint: `endpoints/user.py`
2. Observa cómo usa `Depends(get_user_service)`
3. Sigue el flujo hasta `service/user.py`
4. Lee la documentación de FastAPI: https://fastapi.tiangolo.com/

**Siguiente paso:** Lee [`../service/Resumen.md`](../service/Resumen.md) para entender la lógica de negocio.
