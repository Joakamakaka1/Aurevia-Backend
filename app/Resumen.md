# 📚 Resumen - Carpeta `app/`

## 📋 ¿Qué es este módulo?

La carpeta `app/` contiene **todo el código fuente** de la aplicación Aurevia API. Es el corazón del proyecto donde se implementa la lógica de la API REST.

## 🎯 Responsabilidad

Esta es la **aplicación principal** que:

- Define los endpoints HTTP (rutas de la API)
- Implementa la lógica de negocio
- Maneja la autenticación y seguridad
- Gestiona la conexión con la base de datos
- Valida y serializa datos

## 📁 Estructura de Carpetas

```
app/
├── api/              # 🌐 Endpoints HTTP (capa de presentación)
├── auth/             # 🔐 Autenticación JWT y seguridad
├── core/             # ⚙️ Configuración y utilidades centrales
├── db/               # 💾 Base de datos y modelos ORM
├── repository/       # 📦 Acceso a datos (SQL queries)
├── schemas/          # ✅ Validación con Pydantic
├── service/          # 💼 Lógica de negocio
└── main.py           # 🚀 Punto de entrada de la aplicación
```

## 🔄 Flujo de una Petición (Request Flow)

Cuando un cliente hace una petición HTTP, el flujo es:

```
1️⃣ CLIENT REQUEST
   ↓
   POST /api/v1/trip/
   Body: {"name": "Viaje a París", "country_id": 2, ...}

2️⃣ API LAYER (api/v1/endpoints/trip.py)
   ↓ Router de FastAPI recibe la petición
   ↓ Valida con Pydantic Schema (schemas/trip.py → TripCreate)
   ↓ Inyecta dependencias (service)

3️⃣ SERVICE LAYER (service/trip.py → TripService)
   ↓ Ejecuta lógica de negocio
   ↓ Valida que el país exista
   ↓ Verifica que las fechas sean coherentes
   ↓ Llama al repository

4️⃣ REPOSITORY LAYER (repository/trip.py → TripRepository)
   ↓ Construye la query SQL con SQLAlchemy
   ↓ Hace joinedload para cargar relaciones
   ↓ Ejecuta INSERT en la base de datos

5️⃣ DATABASE LAYER (db/models/trip.py → Trip Model)
   ↓ SQLAlchemy ORM mapea el objeto Python a SQL
   ↓ MySQL ejecuta: INSERT INTO trips VALUES (...)

6️⃣ RESPONSE
   ↓ Repository retorna objeto Trip
   ↓ Service hace commit y retorna Trip
   ↓ Endpoint serializa con Pydantic (TripOut)
   ↓ FastAPI retorna JSON al cliente

   Response: 201 Created
   {"id": 1, "name": "Viaje a París", "country": {...}, ...}
```

## 📦 Módulos Principales

### 🌐 `api/` - Capa de Endpoints

**Qué hace:**

- Define los endpoints HTTP (GET, POST, PUT, DELETE)
- Mapea URLs a funciones
- Recibe y retorna datos JSON

**Ejemplo:**

```python
@router.post("/", response_model=TripOut)
def create_trip(payload: TripCreate, service: TripService = Depends(...)):
    return service.create(...)
```

---

### 🔐 `auth/` - Autenticación y Seguridad

**Qué hace:**

- Genera y valida tokens JWT
- Hashea y verifica contraseñas con Bcrypt
- Proporciona dependencias de autenticación

**Archivos clave:**

- `jwt.py` → Crear/decodificar tokens
- `security.py` → Hash de passwords
- `deps.py` → Dependencias (get_db, get_current_user)

---

### ⚙️ `core/` - Configuración Central

**Qué hace:**

- Lee variables de entorno (.env)
- Maneja excepciones globalmente
- Define constantes y códigos de error
- Proporciona decoradores útiles

**Archivos clave:**

- `config.py` → Settings (DB, JWT, CORS)
- `exceptions.py` → Manejo de errores
- `decorators.py` → @transactional
- `constants.py` → ErrorCode enum

---

### 💾 `db/` - Base de Datos

**Qué hace:**

- Configura SQLAlchemy engine y sesiones
- Define modelos ORM (tablas)
- Hace seeding de datos iniciales

**Archivos clave:**

- `session.py` → Configuración de DB
- `base.py` → Base class para modelos
- `models/` → User, Trip, Country, City, Comment
- `seed.py` → Datos de prueba

---

### 📦 `repository/` - Acceso a Datos

**Qué hace:**

- Encapsula queries SQL
- Usa SQLAlchemy para hacer SELECT, INSERT, UPDATE, DELETE
- Optimiza con joinedload (eager loading)

**Patrón Repository:**
Separa la lógica de acceso a datos de la lógica de negocio.

---

### ✅ `schemas/` - Validación

**Qué hace:**

- Define modelos Pydantic para validar entrada
- Serializa objetos SQLAlchemy a JSON
- Evita referencias circulares con schemas Basic/Out

**Ejemplo:**

```python
class TripCreate(BaseModel):
    name: str
    start_date: date
    end_date: date

    @field_validator('name')
    def validate_name_length(cls, v):
        if len(v) < 3:
            raise ValueError("Muy corto")
        return v
```

---

### 💼 `service/` - Lógica de Negocio

**Qué hace:**

- Implementa reglas de negocio
- Valida datos complejos
- Coordina entre repositories
- Maneja transacciones con @transactional

**Ejemplo:**

```python
@transactional
def create_trip(self, trip_data):
    # Validar que el país existe
    if not self.country_repo.get_by_id(trip_data.country_id):
        raise AppError(404, "País no existe")

    # Validar fechas
    if trip_data.end_date < trip_data.start_date:
        raise AppError(400, "Fechas inválidas")

    # Crear viaje
    return self.trip_repo.create(trip_data)
```

---

## 🚀 `main.py` - Punto de Entrada

Este archivo es el **corazón de la aplicación**. Hace:

```python
# 1. Crear app FastAPI
app = FastAPI(title="Aurevia API")

# 2. Crear tablas en BD
Base.metadata.create_all(bind=engine)

# 3. Hacer seeding (datos iniciales)
seed_db(db)

# 4. Incluir routers
app.include_router(api_router, prefix="/api")

# 5. Configurar manejadores de excepciones
app.add_exception_handler(AppError, app_error_handler)

# 6. Configurar CORS
app.add_middleware(CORSMiddleware, allow_origins=...)
```

## 💡 Conceptos Clave

### 1. Separación de Responsabilidades (SoC)

Cada módulo tiene **una única responsabilidad**:

- API → HTTP
- Service → Negocio
- Repository → Datos
- Models → Estructura

### 2. Dependency Injection (DI)

FastAPI inyecta dependencias automáticamente:

```python
def endpoint(service: UserService = Depends(get_user_service)):
    # 'service' ya está instanciado
```

### 3. Repository Pattern

En vez de poner SQL en services, usamos repositories:

```python
# ❌ Malo (SQL en service)
def get_user(db, user_id):
    return db.query(User).filter(User.id == user_id).first()

# ✅ Bueno (delegado a repository)
def get_user(user_id):
    return self.repo.get_by_id(user_id)
```

### 4. Transactional Decorator

El decorador `@transactional` maneja automáticamente:

- ✅ Commit si todo va bien
- ❌ Rollback si hay error

```python
@transactional
def create_user(self, ...):
    # No necesitas db.commit() manual
    return self.repo.create(user)
```

## 📖 Siguiente Paso

Explora cada submódulo leyendo su `Resumen.md`:

1. Empieza por `db/models/Resumen.md` para ver las entidades
2. Luego `schemas/Resumen.md` para validación
3. Después `repository/Resumen.md` para acceso a datos
4. Sigue con `service/Resumen.md` para lógica de negocio
5. Termina en `api/Resumen.md` para los endpoints
