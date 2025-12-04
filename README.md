# Aurevia API - Travel Social Platform

## 📝 Descripción

API REST para una plataforma social centrada en viajes. Los usuarios pueden crear perfiles, compartir experiencias de viaje, comentar viajes de otros y explorar destinos. Diseñada con FastAPI, JWT authentication, y MySQL.

---

## 🗄️ Modelo de Datos

### Entidades Implementadas

#### **User** (Usuario)

Representa un usuario de la plataforma con autenticación JWT y roles.

**Atributos:**

- `id` (PK, Integer, Auto-increment)
- `email` (String 255, Único, Requerido)
- `username` (String 255, Único, Requerido)
- `hashed_password` (String 255, Requerido) - Hash bcrypt
- `role` (Enum: 'user', 'admin', 'superadmin', Default: 'user')

**Relaciones:**

- Tiene muchos `Trip` (1:N)
- Tiene muchos `Comment` (1:N)

**Validaciones:**

- Username: 3-50 caracteres
- Email: Formato válido (validado por Pydantic)
- Password: Hasheado con bcrypt, truncado a 72 bytes

---

#### **Trip** (Viaje)

Viaje realizado por un usuario a un país.

**Atributos:**

- `id` (PK, Integer, Auto-increment)
- `name` (String 255, Requerido)
- `description` (String 255, Requerido)
- `start_date` (Date, Requerido)
- `end_date` (Date, Requerido)
- `user_id` (FK → User, Requerido)
- `country_id` (FK → Country, Requerido)

**Relaciones:**

- Pertenece a un `User` (N:1)
- Pertenece a un `Country` (N:1)
- Tiene muchos `Comment` (1:N)

**Validaciones:**

- Name: 3-100 caracteres
- Description: 10-500 caracteres
- Fechas: Validación de consistencia (end_date >= start_date)

---

#### **Country** (País)

País que puede ser visitado.

**Atributos:**

- `id` (PK, Integer, Auto-increment)
- `name` (String 255, Único, Requerido)

**Relaciones:**

- Tiene muchos `Trip` (1:N)
- Tiene muchas `City` (1:N)

**Validaciones:**

- Name: 2-100 caracteres
- Nombre único (no duplicados)

---

#### **City** (Ciudad)

Ciudad o localidad específica dentro de un país.

**Atributos:**

- `id` (PK, Integer, Auto-increment)
- `name` (String 255, Único, Requerido)
- `latitude` (Float, Nullable)
- `longitude` (Float, Nullable)
- `country_id` (FK → Country, Nullable)

**Relaciones:**

- Pertenece a un `Country` (N:1)

**Validaciones:**

- Name: 2-100 caracteres
- Nombre único (no duplicados)

---

#### **Comment** (Comentario)

Comentario en un viaje específico.

**Atributos:**

- `id` (PK, Integer, Auto-increment)
- `content` (String 255, Requerido)
- `created_at` (DateTime, Auto-generado)
- `user_id` (FK → User, Requerido)
- `trip_id` (FK → Trip, Requerido)

**Relaciones:**

- Pertenece a un `Trip` (N:1)
- Es escrito por un `User` (N:1)

**Validaciones:**

- Content: 5-200 caracteres

---

## 📊 Diagrama de Relaciones

```
               ┌────────────┐
               │            │
               │    User    │
               │            │
               └────────────┘
               │            │
          ┌─────────────────────────┐
          │                         │
          ▼                         ▼
     ┌──────────┐              ┌──────────┐
     │   Trip   │◄─────────────│ Comment  │
     └──────────┘              └──────────┘
          │
     ┌──────────┐
     │ Country  │
     └──────────┘
          │
          ▼
     ┌──────────┐
     │   City   │
     └──────────┘
```

---

## ✨ Funcionalidades Implementadas

### Autenticación y Seguridad

- ✅ **JWT Authentication** - Tokens con user_id, username y role
- ✅ **Password Hashing** - Bcrypt con salt automático
- ✅ **Role-Based Access** - Roles: user, admin, superadmin
- ✅ **Validación de entrada** - Pydantic schemas con validadores personalizados

### CRUD Completo

- ✅ **Users** - Registro, login, actualización, eliminación
- ✅ **Trips** - Crear, leer, actualizar, eliminar viajes
- ✅ **Comments** - Comentarios por viaje y por usuario
- ✅ **Countries** - Gestión de países
- ✅ **Cities** - Gestión de ciudades con geolocalización

### Manejo de Errores

- ✅ **Errores personalizados** - Códigos y mensajes descriptivos en español
- ✅ **Validación automática** - Errores de Pydantic formateados
- ✅ **Errores de BD** - IntegrityError, OperationalError, DataError
- ✅ **Logging** - Registro de todos los errores
- ✅ **Respuestas consistentes** - Formato JSON estándar

### Arquitectura

- ✅ **Schemas en dos niveles** - Basic (nested) y Out (full response)
- ✅ **Sin imports circulares** - Forward references con TYPE_CHECKING
- ✅ **Validaciones en service layer** - Lógica de negocio centralizada
- ✅ **Variables de entorno** - Credenciales en .env
- ✅ **Seeding automático** - Datos de prueba al iniciar

---

## 🛠️ Tecnologías

| Categoría         | Tecnología       | Versión       |
| ----------------- | ---------------- | ------------- |
| **Framework**     | FastAPI          | Latest        |
| **Base de Datos** | MySQL            | 8.0+          |
| **ORM**           | SQLAlchemy       | 2.x           |
| **Validación**    | Pydantic         | 2.x           |
| **Auth**          | PyJWT            | 2.10.1        |
| **Password**      | Bcrypt + Passlib | 3.2.2 - 1.7.4 |
| **Env Vars**      | python-dotenv    | 1.2.1         |

---

## 📦 Instalación

### 1. Clonar repositorio

```bash
git clone <repository-url>
cd Aurevia_API-v.01
```

### 2. Crear entorno virtual

```bash
python -m venv venv
```

### 3. Activar entorno virtual

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/Mac:**

```bash
source venv/bin/activate
```

### 4. Instalar dependencias

```bash
# Framework y servidor
pip install fastapi uvicorn

# Base de datos
pip install mysql-connector-python
pip install sqlalchemy

# Validación y seguridad
pip install "pydantic[email]"
pip install passlib
pip install bcrypt
pip install pyjwt

# Utilidades
pip install python-dotenv
pip install requests
```

### 5. Configurar variables de entorno

Copia `.env.example` a `.env` y configura tus credenciales:

```bash
cp .env.example .env
```

Edita `.env`:

```env
# Database
MYSQL_USER=root
MYSQL_PASSWORD=tu_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=aurevia

# JWT
SECRET_KEY=tu-clave-secreta-muy-larga-minimo-32-caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
ALLOWED_ORIGINS=http://localhost:8100,http://127.0.0.1:8100

# App
ENVIRONMENT=development
DEBUG=True
```

**⚠️ IMPORTANTE:** Genera una SECRET_KEY segura:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 6. Crear base de datos

```sql
CREATE DATABASE aurevia CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## 🚀 Uso

### Iniciar servidor

**Modo normal:**

```bash
uvicorn app.main:app
```

**Modo desarrollo (con recarga automática):**

```bash
uvicorn app.main:app --reload
```

**Especificar puerto:**

```bash
uvicorn app.main:app --port 8080
```

El servidor estará disponible en: `http://localhost:8000`

### Documentación API

FastAPI genera documentación interactiva automáticamente:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI Schema:** `http://localhost:8000/openapi.json`

---

## 🔑 Endpoints Principales

### Autenticación (`/api/v1/auth`)

| Método | Endpoint               | Descripción                  | Body                                    |
| ------ | ---------------------- | ---------------------------- | --------------------------------------- |
| POST   | `/register`            | Registrar usuario            | `{email, username, password, role?}`    |
| POST   | `/login`               | Login y obtener JWT          | `{email, password}`                     |
| GET    | `/`                    | Listar todos los usuarios    | -                                       |
| GET    | `/id/{user_id}`        | Obtener usuario por ID       | -                                       |
| GET    | `/email/{email}`       | Obtener usuario por email    | -                                       |
| GET    | `/username/{username}` | Obtener usuario por username | -                                       |
| PUT    | `/{user_id}`           | Actualizar usuario           | `{email?, username?, password?, role?}` |
| DELETE | `/{user_id}`           | Eliminar usuario             | -                                       |

### Viajes (`/api/v1/trip`)

| Método | Endpoint     | Descripción             | Body                                                             |
| ------ | ------------ | ----------------------- | ---------------------------------------------------------------- |
| GET    | `/`          | Listar todos los viajes | -                                                                |
| GET    | `/{trip_id}` | Obtener viaje por ID    | -                                                                |
| POST   | `/`          | Crear viaje             | `{name, description, start_date, end_date, user_id, country_id}` |
| PUT    | `/{trip_id}` | Actualizar viaje        | `{name?, description?, start_date?, end_date?, country_id?}`     |
| DELETE | `/{trip_id}` | Eliminar viaje          | -                                                                |

### Comentarios (`/api/v1/comment`)

| Método | Endpoint          | Descripción                  | Body                          |
| ------ | ----------------- | ---------------------------- | ----------------------------- |
| GET    | `/`               | Listar todos los comentarios | -                             |
| GET    | `/{comment_id}`   | Obtener comentario por ID    | -                             |
| GET    | `/user/{user_id}` | Comentarios de un usuario    | -                             |
| GET    | `/trip/{trip_id}` | Comentarios de un viaje      | -                             |
| POST   | `/`               | Crear comentario             | `{content, user_id, trip_id}` |
| PUT    | `/{comment_id}`   | Actualizar comentario        | `{content?}`                  |
| DELETE | `/{comment_id}`   | Eliminar comentario          | -                             |

### Países (`/api/v1/country`)

| Método | Endpoint               | Descripción             | Body      |
| ------ | ---------------------- | ----------------------- | --------- |
| GET    | `/`                    | Listar todos los países | -         |
| GET    | `/id/{country_id}`     | Obtener país por ID     | -         |
| GET    | `/name/{country_name}` | Obtener país por nombre | -         |
| POST   | `/`                    | Crear país              | `{name}`  |
| PUT    | `/{country_id}`        | Actualizar país         | `{name?}` |
| DELETE | `/{country_id}`        | Eliminar país           | -         |

### Ciudades (`/api/v1/city`)

| Método | Endpoint            | Descripción               | Body                                          |
| ------ | ------------------- | ------------------------- | --------------------------------------------- |
| GET    | `/`                 | Listar todas las ciudades | -                                             |
| GET    | `/id/{city_id}`     | Obtener ciudad por ID     | -                                             |
| GET    | `/name/{city_name}` | Obtener ciudad por nombre | -                                             |
| POST   | `/`                 | Crear ciudad              | `{name, latitude?, longitude?, country_id}`   |
| PUT    | `/{city_id}`        | Actualizar ciudad         | `{name?, latitude?, longitude?, country_id?}` |
| DELETE | `/{city_id}`        | Eliminar ciudad           | -                                             |

---

## 🔐 Autenticación JWT

### Registro

```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword123",
  "role": "user"  // Opcional, default: "user"
}
```

### Login

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Respuesta:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "role": "user",
    "trips": [],
    "comments": []
  }
}
```

### Usar el Token

```bash
GET /api/v1/trip/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Decodificar Token

El token JWT contiene:

```json
{
  "user_id": 1,
  "username": "johndoe",
  "role": "user",
  "exp": 1733425200
}
```

Puedes decodificarlo en: https://jwt.io

---

## 🗃️ Seeding

La base de datos se puebla automáticamente al iniciar el servidor (si está activado en `main.py`):

- **5 usuarios** (1 admin, 4 users) - Password: `password123`
- **5 países** (Spain, France, Italy, Japan, USA)
- **10 ciudades** (2 por país con coordenadas aleatorias)
- **10 viajes** (2 por usuario)
- **30 comentarios** (3 por viaje)

Para desactivar el seeding, comenta las líneas en `app/main.py`:

```python
# try:
#     db = SessionLocal()
#     seed_db(db)
# finally:
#     db.close()
```

---

## 📂 Estructura del Proyecto

```
Aurevia_API-v.01/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           ├── user.py
│   │           ├── trip.py
│   │           ├── comment.py
│   │           ├── country.py
│   │           └── city.py
│   ├── auth/
│   │   ├── deps.py         # Dependencias (get_db)
│   │   ├── jwt.py          # JWT utilities
│   │   └── security.py     # Password hashing
│   ├── core/
│   │   ├── config.py       # Settings (desde .env)
│   │   └── exceptions.py   # Error handlers
│   ├── db/
│   │   ├── base.py         # Base class
│   │   ├── session.py      # DB session
│   │   ├── seed.py         # Seeding data
│   │   └── models/
│   │       ├── user.py
│   │       ├── trip.py
│   │       ├── comment.py
│   │       ├── country.py
│   │       └── city.py
│   ├── schemas/
│   │   ├── user.py         # Pydantic models
│   │   ├── trip.py
│   │   ├── comment.py
│   │   ├── country.py
│   │   └── city.py
│   ├── service/
│   │   ├── user.py         # Business logic
│   │   ├── trip.py
│   │   ├── comment.py
│   │   ├── country.py
│   │   └── city.py
│   └── main.py             # FastAPI app
├── .env                    # Environment variables (NOT in git)
├── .env.example            # Template
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🐛 Manejo de Errores

Todos los errores retornan un formato consistente:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Mensaje descriptivo en español",
    "type": "error_type"
  },
  "details": {
    // Detalles específicos del error
  },
  "path": "/api/v1/endpoint"
}
```

### Códigos de Error Comunes

| Código                | Descripción                     |
| --------------------- | ------------------------------- |
| `VALIDATION_ERROR`    | Error de validación de Pydantic |
| `USER_NOT_FOUND`      | Usuario no encontrado           |
| `EMAIL_DUPLICATED`    | Email ya registrado             |
| `USERNAME_DUPLICATED` | Username ya registrado          |
| `INVALID_PASSWORD`    | Contraseña incorrecta           |
| `EMAIL_NOT_FOUND`     | Email no existe                 |
| `TRIP_NOT_FOUND`      | Viaje no encontrado             |
| `COUNTRY_NOT_FOUND`   | País no encontrado              |
| `CITY_NOT_FOUND`      | Ciudad no encontrada            |
| `COMMENT_NOT_FOUND`   | Comentario no encontrado        |

---

## 🔮 Funcionalidades Futuras

- 🔜 Middleware de autenticación JWT para endpoints protegidos
- 🔜 Refresh tokens
- 🔜 Subida de fotos de viajes (S3/Cloudinary)
- 🔜 Sistema de likes en viajes
- 🔜 Búsqueda y filtrado avanzado con IA
- 🔜 Paginación en listados
- 🔜 Rate limiting
- 🔜 Tests unitarios e integración
- 🔜 Docker, Docker Compose y Kubernetes
- 🔜 CI/CD Pipeline

---

## 📄 Licencia

Este proyecto es privado y de uso educativo.

---

## 👥 Autor

Desarrollado como proyecto de aprendizaje de FastAPI y arquitectura de APIs REST.
