# Travel Social Platform

## Descripción

Plataforma social centrada en los viajes, diseñada para fomentar la interacción entre personas a través de sus experiencias viajeras. Los usuarios pueden crear perfiles, compartir viajes realizados y publicar información útil sobre cada destino. El objetivo es crear una comunidad colaborativa donde los viajes sirvan como punto de encuentro, intercambio cultural e inspiración mutua para descubrir el mundo.

## Modelo de Datos

### Entidades Principales

#### **User**

Usuario de la plataforma.

**Atributos:**

- `id` (PK)
- `username` (único)
- `email` (único)
- `hashed_password` (hash)
- `profile_photo` (URL/path, opcional)
- `bio` (texto corto, opcional)
- `created_at` (timestamp)
- `updated_at` (timestamp)

**Relaciones:**

- Tiene muchos `Trip` (1:N)
- Tiene muchas `Friendship` (1:N)
- Escribe muchos `Comment` (1:N)

---

#### **Trip**

Viaje realizado por un usuario.

**Atributos:**

- `id` (PK)
- `user_id` (FK → User)
- `country_id` (FK → Country)
- `title` (nombre del viaje)
- `description` (texto largo, opcional)
- `start_date` (fecha)
- `end_date` (fecha)
- `photos` (array de URLs)
- `created_at` (timestamp)

**Relaciones:**

- Pertenece a un `User` (N:1)
- Pertenece a un `Country` (N:1)
- Tiene muchos `Comment` (1:N)

---

#### **Country**

País visitado.

**Atributos:**

- `id` (PK)
- `name` (único)
- `code` (ISO código, ej: "ES", "FR", único)
- `flag` (URL/emoji, opcional)

**Relaciones:**

- Tiene muchos `Trip` (1:N)
- Tiene muchas `City` (1:N)

---

#### **City**

Ciudad o localidad específica dentro de un país.

**Atributos:**

- `id` (PK)
- `name`
- `country_id` (FK → Country)
- `latitude` (para mapa futuro)
- `longitude` (para mapa futuro)

**Relaciones:**

- Pertenece a un `Country` (N:1)

---

#### **Comment**

Comentario en un viaje.

**Atributos:**

- `id` (PK)
- `trip_id` (FK → Trip)
- `user_id` (FK → User)
- `content` (texto)
- `created_at` (timestamp)

**Relaciones:**

- Pertenece a un `Trip` (N:1)
- Es escrito por un `User` (N:1)

---

#### **Friendship**

Relación de amistad entre usuarios.

**Atributos:**

- `id` (PK)
- `user_id` (FK → User) - quien envía la solicitud
- `friend_id` (FK → User) - quien recibe la solicitud
- `status` (enum: 'pending', 'accepted', 'rejected')
- `created_at` (timestamp)
- `updated_at` (timestamp)

**Relaciones:**

- Conecta dos `User` (N:1 con user_id, N:1 con friend_id)

---

## Diagrama de Relaciones

```
                    ┌─────────┐
                    │  User   │
                    └─────────┘
                         │
           ┌─────────────┼─────────────┐
           │             │             │
           ▼             ▼             ▼
    ┌───────────┐  ┌─────────┐  ┌───────────┐
    │Friendship │  │  Trip   │  │ Comment   │
    └───────────┘  └─────────┘  └───────────┘
                         │             ▲
                         ▼             │
                    ┌─────────┐        │
                    │ Country │        │
                    └─────────┘        │
                         │             │
                         ▼             │
                    ┌─────────┐        │
                    │  City   │        │
                    └─────────┘        │
                                       │
                         Trip ─────────┘
```

## Funcionalidades Principales

- ✅ Creación de perfiles de usuario
- ✅ Publicación de viajes con fotos y descripciones
- ✅ Asociación de viajes a países
- ✅ Sistema de comentarios en viajes
- ✅ Sistema de amistades entre usuarios
- 🔜 Mapa interactivo mundial (funcionalidad futura)

## Tecnologías

- **Backend:** FastAPI
- **Base de datos:** MySQL
- **ORM:** SQLAlchemy
- **Validación:** Pydantic
- **Autenticación:** Passlib

## APIs Externas

### REST Countries API

Utilizada para poblar la base de datos con información de países.

- **URL:** https://restcountries.com/
- **Uso:** Obtener listado completo de países con sus códigos ISO y banderas
- **Gratuita:** Sí, sin necesidad de API key
- **Datos obtenidos:** Nombre, código ISO (alpha2), bandera (emoji/URL)

### GeoNames API

Utilizada para poblar la base de datos con ciudades del mundo.

- **URL:** http://www.geonames.org/
- **Uso:** Obtener ciudades por país con coordenadas geográficas
- **Requiere registro:** Sí (gratuito)
- **Datos obtenidos:** Nombre de ciudad, coordenadas (latitud, longitud), jerarquía administrativa

## Instalación

### 1. Crear entorno virtual

```bash
python -m venv venv
```

### 2. Activar entorno virtual

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/Mac:**

```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
# FastAPI y servidor
pip install fastapi uvicorn

# Base de datos
pip install mysql-connector-python
pip install sqlalchemy

# Validación y seguridad
pip install "pydantic[email]"
pip install passlib
pip install bcrypt

# Para consumir APIs externas
pip install requests
```

## Uso

### Iniciar el servidor

**Modo normal:**

```bash
uvicorn app.main:app
```

**Modo desarrollo (con recarga automática):**

```bash
uvicorn main:app --reload
```

El servidor estará disponible en: `http://localhost:8000`

Documentación API automática: `http://localhost:8000/docs`
