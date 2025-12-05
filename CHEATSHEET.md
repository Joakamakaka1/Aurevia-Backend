# 🚀 Aurevia API - Cheatsheet

Referencia rápida para desarrollo y uso de la API Aurevia.

---

## 📦 Setup Rápido

### Local (Python)

```bash
# 1. Clonar y entrar al proyecto
git clone <repo-url>
cd Aurevia_API-v.01

# 2. Crear y activar venv
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar .env
cp .env.example .env
# Editar .env con tus credenciales

# 5. Crear BD en MySQL
mysql -u root -p
CREATE DATABASE aurevia CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit

# 6. Iniciar servidor
uvicorn app.main:app --reload
```

### Docker Compose (Recomendado)

```bash
# 1. Configurar .env
cp .env.example .env

# 2. Levantar todo (API + MySQL)
docker-compose up --build -d

# 3. Ver logs
docker-compose logs -f

# 4. Detener
docker-compose down
```

---

## 🔑 Endpoints Principales

### Base URL

```
http://localhost:8000
```

### 1️⃣ Autenticación

#### Registro

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepass123",
    "role": "user"
  }'
```

#### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

**Respuesta:**

```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": { "id": 1, "email": "...", "username": "..." }
}
```

#### Usar Token

```bash
curl -X GET http://localhost:8000/api/v1/trip/ \
  -H "Authorization: Bearer eyJhbGc..."
```

### 2️⃣ Viajes (Trips)

```bash
# Listar viajes
GET /api/v1/trip/

# Obtener viaje por ID
GET /api/v1/trip/1

# Crear viaje
POST /api/v1/trip/
{
  "name": "Viaje a España",
  "description": "Recorrido por Madrid y Barcelona",
  "start_date": "2024-06-01",
  "end_date": "2024-06-15",
  "user_id": 1,
  "country_id": 1
}

# Actualizar viaje
PUT /api/v1/trip/1
{
  "name": "Viaje a España Actualizado",
  "end_date": "2024-06-20"
}

# Eliminar viaje
DELETE /api/v1/trip/1
```

### 3️⃣ Comentarios

```bash
# Comentarios de un viaje
GET /api/v1/comment/trip/1

# Comentarios de un usuario
GET /api/v1/comment/user/1

# Crear comentario
POST /api/v1/comment/
{
  "content": "¡Increíble viaje!",
  "user_id": 1,
  "trip_id": 1
}
```

### 4️⃣ Healthcheck

```bash
curl http://localhost:8000/api/v1/healthy
```

---

## 💻 Comandos de Desarrollo

### Gestión de Servidor

```bash
# Iniciar con auto-reload
uvicorn app.main:app --reload

# Iniciar en puerto específico
uvicorn app.main:app --reload --port 8080

# Iniciar con host público
uvicorn app.main:app --reload --host 0.0.0.0

# Sin echo de SQL (mejor rendimiento)
# Editar app/db/session.py: echo=False
```

### Base de Datos

```bash
# Conectar a MySQL local
mysql -u root -p aurevia

# Conectar a MySQL de Docker
mysql -h 127.0.0.1 -P 3307 -u root -p

# Ver tablas
SHOW TABLES;

# Limpiar BD (re-seed)
DROP DATABASE aurevia;
CREATE DATABASE aurevia CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
# Reiniciar uvicorn (auto-crea tablas y seed)

# Entrar al contenedor MySQL
docker exec -it aurevia_db mysql -u root -p
```

### Gestión de Dependencias

```bash
# Ver dependencias instaladas
pip list

# Ver dependencias en formato requirements
pip freeze

# Actualizar requirements.txt
pip freeze > requirements.txt

# Instalar una nueva dependencia
pip install paquete
pip freeze > requirements.txt
```

### Docker

```bash
# Ver contenedores
docker ps -a

# Logs de API
docker-compose logs -f api

# Logs de MySQL
docker-compose logs -f db

# Reconstruir solo API
docker-compose build api
docker-compose up -d api

# Detener sin borrar datos
docker-compose stop

# Detener y borrar todo (⚠️ incluye datos BD)
docker-compose down -v

# Ver volúmenes
docker volume ls

# Limpiar todo Docker
docker system prune -a --volumes
```

---

## 🧩 Snippets de Código Útiles

### Crear un Nuevo Endpoint

```python
# app/api/v1/endpoints/tu_endpoint.py
from fastapi import APIRouter, Depends
from app.service.tu_servicio import TuServicio
from app.api.deps import get_tu_servicio
from app.schemas.tu_schema import TuOut

router = APIRouter(prefix="/v1/tu-recurso", tags=["Tu Recurso"])

@router.get("/", response_model=list[TuOut])
def get_all(service: TuServicio = Depends(get_tu_servicio)):
    return service.get_all()
```

### Crear un Nuevo Servicio

```python
# app/service/tu_servicio.py
from sqlalchemy.orm import Session
from app.repository.tu_repo import TuRepository
from app.core.decorators import transactional
from app.core.exceptions import AppError
from app.core.constants import ErrorCode

class TuServicio:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TuRepository(db)

    def get_all(self):
        return self.repo.get_all()

    @transactional
    def create(self, data):
        # Validaciones de negocio aquí
        if existe_duplicado:
            raise AppError(409, ErrorCode.DUPLICADO, "Ya existe")

        return self.repo.create(data)
```

### Crear un Nuevo Repository

```python
# app/repository/tu_repo.py
from sqlalchemy.orm import Session
from app.db.models.tu_modelo import TuModelo

class TuRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(TuModelo).all()

    def get_by_id(self, id: int):
        return self.db.query(TuModelo).filter(TuModelo.id == id).first()

    def create(self, entity):
        self.db.add(entity)
        return entity
```

### Crear un Schema Pydantic

```python
# app/schemas/tu_schema.py
from pydantic import BaseModel, Field
from typing import Optional

class TuBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    descripcion: Optional[str] = None

class TuCreate(TuBase):
    pass

class TuUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3)
    descripcion: Optional[str] = None

class TuOut(TuBase):
    id: int

    class Config:
        from_attributes = True
```

### Lanzar AppError Personalizado

```python
from app.core.exceptions import AppError
from app.core.constants import ErrorCode

# En tu servicio
if not usuario:
    raise AppError(404, ErrorCode.USER_NOT_FOUND, "Usuario no encontrado")

if email_duplicado:
    raise AppError(409, ErrorCode.EMAIL_DUPLICATED, "Email ya registrado")

if datos_invalidos:
    raise AppError(400, ErrorCode.INVALID_DATA, "Datos inválidos")
```

---

## 🐛 Troubleshooting

### La API no inicia

```bash
# Verificar que el puerto 8000 no esté ocupado
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Matar proceso en puerto 8000 (Windows)
taskkill /F /PID <PID>

# Cambiar puerto
uvicorn app.main:app --port 8080
```

### Error de conexión a MySQL

```bash
# Verificar que MySQL esté corriendo
# Windows
net start MySQL80

# Linux
sudo systemctl status mysql

# Verificar credenciales en .env
MYSQL_USER=root
MYSQL_PASSWORD=tu_password
MYSQL_HOST=localhost  # o 'db' para Docker
MYSQL_PORT=3306
MYSQL_DB=aurevia
```

### Error "Table doesn't exist"

```python
# La aplicación crea tablas automáticamente al iniciar
# Si hay errores, verifica:
# 1. Que la BD exista
# 2. Que las credenciales en .env sean correctas
# 3. Reinicia uvicorn

# Forzar recreación (⚠️ borra datos)
DROP DATABASE aurevia;
CREATE DATABASE aurevia CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
# Reinicia uvicorn
```

### Imports circulares

```python
# Usa TYPE_CHECKING para forward references
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.otro import OtroSchema

class MiSchema(BaseModel):
    # Usa string en lugar de clase directa
    otros: list["OtroSchema"] = []
```

### Error de validación Pydantic

```python
# Asegúrate de usar model_dump() en lugar de dict()
# Pydantic v2
data = schema.model_dump(exclude_unset=True)

# Para excluir campos None
data = schema.model_dump(exclude_none=True)
```

---

## 🎯 Mejores Prácticas

### Arquitectura en Capas

```
Request → Endpoint → Service → Repository → Database
         ↓           ↓          ↓
      Validación  Lógica de  Solo CRUD
      Pydantic    Negocio
```

**Reglas:**

- ✅ **Endpoints**: Solo routing y validación de entrada (Pydantic)
- ✅ **Services**: Toda la lógica de negocio y validaciones complejas
- ✅ **Repositories**: Solo acceso a datos (CRUD), sin lógica de negocio
- ✅ **Models**: Definición de tablas SQLAlchemy

### Manejo de Transacciones

```python
# Usa @transactional en servicios que modifican BD
from app.core.decorators import transactional

class MiServicio:
    @transactional  # Auto commit/rollback
    def create(self, data):
        entity = self.repo.create(data)
        return entity
```

### Validaciones

```python
# En el SERVICIO, no en el repositorio
class UserService:
    @transactional
    def create(self, email, password):
        # ✅ Validar duplicados
        if self.repo.get_by_email(email):
            raise AppError(409, ErrorCode.EMAIL_DUPLICATED, "Email existe")

        # ✅ Validar lógica de negocio
        if len(password) < 8:
            raise AppError(400, ErrorCode.WEAK_PASSWORD, "Contraseña débil")

        # Hash y creación
        hashed = hash_password(password)
        return self.repo.create(User(email=email, hashed_password=hashed))
```

### Eager Loading (Prevenir N+1)

```python
# ✅ BUENO: Cargar relaciones de una vez
from sqlalchemy.orm import joinedload

def get_all(self):
    return (
        self.db.query(User)
        .options(joinedload(User.trips), joinedload(User.comments))
        .all()
    )

# ❌ MALO: Lazy loading causa N+1
def get_all(self):
    return self.db.query(User).all()
    # Al acceder a user.trips se hace otra query por cada usuario
```

### Variables de Entorno

```python
# ✅ SIEMPRE usar .env para secrets
from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
DATABASE_URL = settings.database_url

# ❌ NUNCA hardcodear credenciales
SECRET_KEY = "mi-clave-secreta"  # MAL
```

### Schemas Pydantic

```python
# Dos niveles: Basic (nested) y Out (completo)

# Para incluir en otros schemas (evita recursión)
class UserBasic(BaseModel):
    id: int
    username: str

# Para respuestas completas
class UserOut(UserBasic):
    email: str
    trips: list[TripBasic] = []
    comments: list[CommentBasic] = []
```

---

## 📚 Recursos FastAPI

### Documentación Interactiva

```
http://localhost:8000/docs     # Swagger UI
http://localhost:8000/redoc    # ReDoc
http://localhost:8000/openapi.json  # Schema JSON
```

### Dependency Injection

```python
# Crear dependencia reutilizable
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    return get_user(payload["user_id"])

# Usar en endpoint
@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return user
```

### Query Parameters

```python
from typing import Optional

@router.get("/items/")
def get_items(
    skip: int = 0,              # Default value
    limit: int = 10,
    search: Optional[str] = None  # Opcional
):
    return items[skip:skip+limit]
```

### Path Parameters con Validación

```python
from pydantic import Field

@router.get("/users/{user_id}")
def get_user(
    user_id: int = Path(..., gt=0)  # Mayor que 0
):
    return {"user_id": user_id}
```

### Response Models

```python
from typing import List

@router.get("/users/", response_model=List[UserOut])
def get_users():
    return users  # Automáticamente serializa a UserOut

@router.post("/users/", response_model=UserOut, status_code=201)
def create_user(user: UserCreate):
    return created_user
```

---

## 🔐 Seguridad

### JWT Token Generation

```python
from app.auth.jwt import create_access_token

token = create_access_token(
    data={
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }
)
```

### Password Hashing

```python
from app.auth.security import hash_password, verify_password

# Al registrar
hashed = hash_password("plaintext_password")

# Al autenticar
is_valid = verify_password("plaintext_password", hashed_from_db)
```

### Generar SECRET_KEY Segura

```bash
# Python
python -c "import secrets; print(secrets.token_hex(32))"

# OpenSSL
openssl rand -hex 32
```

---

## 🧪 Testing (Futuro)

### Setup de Tests

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_user():
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
```

### Test de Endpoint

```python
# tests/test_auth.py
def test_register_user(client, test_user):
    response = client.post("/api/v1/auth/register", json=test_user)
    assert response.status_code == 201
    assert response.json()["email"] == test_user["email"]

def test_login(client, test_user):
    # Register first
    client.post("/api/v1/auth/register", json=test_user)

    # Login
    response = client.post("/api/v1/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

---

## 🚢 Despliegue (Futuro)

### Variables de Entorno en Producción

```env
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<clave-muy-larga-y-segura>
MYSQL_HOST=your-production-db.com
ALLOWED_ORIGINS=https://your-frontend.com
```

### Docker en Producción

```bash
# Construir para producción
docker build -t aurevia-api:latest .

# Run con variables de producción
docker run -p 80:8000 --env-file .env.production aurevia-api:latest
```

---

## 💡 Tips Rápidos

1. **Usa `--reload` solo en desarrollo** - En producción no es necesario
2. **`echo=True` en SQLAlchemy es útil para debug** - Desactívalo en producción
3. **Seedea datos solo si la BD está vacía** - Ya implementado en `seed.py`
4. **Usa `exclude_unset=True`** - Para updates parciales con Pydantic
5. **Validaciones complejas en servicios** - No en schemas ni repositorios
6. **Un servicio por entidad** - Mantén la separación de responsabilidades
7. **Commits automáticos con @transactional** - No hagas commit manual
8. **Type hints siempre** - Mejora autocompletado y detección de errores
9. **Documenta endpoints con docstrings** - Aparecen en Swagger
10. **CORS configurado desde .env** - Ajusta según tu frontend

---

## 📞 Datos de Seeding

Al iniciar, la API crea automáticamente:

- **5 usuarios** (1 admin, 4 users)
- **Password por defecto**: `password123`
- **5 países**: Spain, France, Italy, Japan, USA
- **10 ciudades** (2 por país)
- **10 viajes** (2 por usuario)
- **30 comentarios** (3 por viaje)

---

**¿Dudas?** Revisa `/docs` para documentación interactiva completa 🚀
