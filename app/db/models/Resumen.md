# 📚 Resumen - Carpeta `app/db/models/`

## 📋 ¿Qué es este módulo?

La carpeta `app/db/models/` contiene los **modelos ORM** (Object-Relational Mapping) de SQLAlchemy. Cada modelo es una **clase Python que representa una tabla** en la base de datos MySQL.

## 🎯 Responsabilidad

Este módulo es responsable de:

- ✅ Definir la estructura de las tablas (columnas, tipos de datos)
- ✅ Establecer relaciones entre tablas (FK, 1:N, N:M)
- ✅ Configurar cascadas (delete, update)
- ✅ Definir restricciones (unique, nullable, etc.)

**⚠️ Los modelos NO contienen:**

- ❌ Lógica de negocio (va en `service/`)
- ❌ Queries SQL (va en `repository/`)
- ❌ Validación de entrada (va en `schemas/`)

## 📁 Modelos Implementados

```
models/
├── __init__.py      # Importa todos los modelos
├── user.py          # 👤 Usuario (autenticación, perfil)
├── trip.py          # ✈️ Viaje (experiencia de viaje)
├── country.py       # 🌍 País (destino)
├── city.py          # 🏙️ Ciudad (ubicación específica)
├── comment.py       # 💬 Comentario (en un viaje)
└── friendship.py    # 🤝 Amistad (comentado, no usado)
```

## 🛠️ Tecnologías Usadas

| Tecnología         | Propósito                         |
| ------------------ | --------------------------------- |
| **SQLAlchemy ORM** | Mapear clases Python → tablas SQL |
| **Mapped**         | Tipado moderno de columnas        |
| **relationship()** | Definir relaciones entre tablas   |
| **ForeignKey**     | Claves foráneas (relaciones)      |

## 📊 Diagrama de Relaciones

```
         ┌─────────────┐
         │    User     │
         │  (Usuario)  │
         └──────┬──────┘
                │ 1
                │
      ┌─────────┴─────────┐
      │                   │
      │ N                 │ N
┌─────▼─────┐       ┌─────▼─────┐
│   Trip    │       │  Comment  │
│ (Viaje)   │       │(Comentario)│
└─────┬─────┘       └─────┬─────┘
      │ N                 │ N
      │                   │
      │ 1                 │ 1
┌─────▼─────┐       ┌─────▼─────┐
│  Country  │◄──────│   Trip    │
│  (País)   │  1:N  │           │
└─────┬─────┘       └───────────┘
      │ 1
      │
      │ N
┌─────▼─────┐
│   City    │
│ (Ciudad)  │
└───────────┘
```

**Lectura del diagrama:**

- `User` 1:N `Trip` → Un usuario tiene muchos viajes
- `User` 1:N `Comment` → Un usuario escribe muchos comentarios
- `Country` 1:N `City` → Un país tiene muchas ciudades
- `Country` 1:N `Trip` → Un país recibe muchos viajes
- `Trip` 1:N `Comment` → Un viaje tiene muchos comentarios

## 📝 Modelos en Detalle

### 1️⃣ `user.py` - Usuario

```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum

class User(Base):
    __tablename__ = "users"

    # Columnas
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        Enum("user", "admin", "superadmin", name="user_role_enum"),
        nullable=False,
        default="user"
    )

    # Relaciones
    trips = relationship("Trip", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
```

**Tabla SQL generada:**

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin', 'superadmin') DEFAULT 'user' NOT NULL,
    INDEX idx_id (id)
);
```

**Características:**

- ✅ Autenticación con password hasheada
- ✅ Roles: `user`, `admin`, `superadmin`
- ✅ Email y username únicos
- ✅ Cascade delete: si eliminas user → se eliminan sus trips y comments

---

### 2️⃣ `trip.py` - Viaje

```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Date, ForeignKey
from datetime import date

class Trip(Base):
    __tablename__ = "trips"

    # Columnas
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Foreign Keys
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"), nullable=False)

    # Relaciones
    user = relationship("User", back_populates="trips")
    country = relationship("Country", back_populates="trips")
    comments = relationship("Comment", back_populates="trip", cascade="all, delete-orphan")
```

**Tabla SQL:**

```sql
CREATE TABLE trips (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    user_id INT NOT NULL,
    country_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (country_id) REFERENCES countries(id)
);
```

**Validaciones (en schema):**

- `start_date` ≤ `end_date`
- `name`: 3-100 caracteres
- `description`: 10-500 caracteres

---

### 3️⃣ `country.py` - País

```python
class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    # Relaciones
    cities = relationship("City", back_populates="country", cascade="all, delete-orphan")
    trips = relationship("Trip", back_populates="country")
```

**Características:**

- ✅ Nombre único (no duplicados)
- ✅ Tiene muchas ciudades
- ✅ Recibe muchos viajes

---

### 4️⃣ `city.py` - Ciudad

```python
from typing import Optional

class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(nullable=True)

    # Foreign Key
    country_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("countries.id"),
        nullable=True
    )

    # Relación
    country = relationship("Country", back_populates="cities")
```

**Características:**

- ✅ Coordenadas geográficas opcionales
- ✅ Puede no tener país asignado (nullable)

---

### 5️⃣ `comment.py` - Comentario

```python
from datetime import datetime

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    # Foreign Keys
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id"), nullable=False)

    # Relaciones
    user = relationship("User", back_populates="comments")
    trip = relationship("Trip", back_populates="comments")
```

**Características:**

- ✅ Timestamp automático al crear
- ✅ Pertenece a un usuario y un viaje
- ✅ Content: 5-200 caracteres (validado en schema)

## 💡 Conceptos Clave

### 1. **ORM Mapping**

```python
# Clase Python
class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255))

# ↕ SQLAlchemy traduce

# SQL
CREATE TABLE users (
    id INT PRIMARY KEY,
    email VARCHAR(255)
);
```

### 2. **Relaciones (Relationships)**

#### **1:N (One-to-Many)**

```python
class User(Base):
    trips = relationship("Trip", back_populates="user")
    # Un user → muchos trips

class Trip(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user = relationship("User", back_populates="trips")
    # Un trip → un user
```

**Uso:**

```python
user = db.query(User).first()
print(user.trips)  # Lista de trips del usuario

trip = db.query(Trip).first()
print(trip.user)   # Usuario dueño del trip
```

#### **back_populates**

Mantiene sincronizadas ambas direcciones:

```python
user.trips.append(trip)  # Agrega trip a user
print(trip.user)         # Automáticamente user asignado
```

### 3. **Cascade (Eliminación en Cascada)**

```python
trips = relationship("Trip", cascade="all, delete-orphan")
```

**Comportamiento:**

```python
# Eliminar user
db.delete(user)
db.commit()

# → Automáticamente elimina todos sus trips y comments
# DELETE FROM trips WHERE user_id = ?
# DELETE FROM comments WHERE user_id = ?
# DELETE FROM users WHERE id = ?
```

**Opciones de cascade:**

- `all` → Propagar todas las operaciones
- `delete` → Eliminar hijos al eliminar padre
- `delete-orphan` → Eliminar hijos si se quitan de la relación

### 4. **Eager Loading vs Lazy Loading**

#### **Lazy Loading (por defecto)**

```python
user = db.query(User).first()      # 1 query: SELECT * FROM users
print(user.trips)                   # 2nd query: SELECT * FROM trips WHERE user_id = ?
```

#### **Eager Loading (joinedload)**

```python
from sqlalchemy.orm import joinedload

user = db.query(User).options(joinedload(User.trips)).first()
# 1 query: SELECT * FROM users JOIN trips ON ...
print(user.trips)  # Ya cargado, sin query extra
```

### 5. **Mapped Types (SQLAlchemy 2.x)**

```python
# Requerido
id: Mapped[int] = mapped_column(primary_key=True)

# Opcional
age: Mapped[Optional[int]] = mapped_column(nullable=True)

# String con longitud
email: Mapped[str] = mapped_column(String(255))

# Enum
role: Mapped[str] = mapped_column(Enum("user", "admin"))

# Date/DateTime
created: Mapped[datetime] = mapped_column(default=func.now())
```

## 🔗 Relación con Otros Módulos

```
┌──────────────┐
│  db/models/  │  ← ESTÁS AQUÍ (estructura de tablas)
└──────┬───────┘
       │ Usado por
       ↓
┌──────────────┐
│ repository/  │  ← Hace queries con los modelos
└──────┬───────┘
       │ Retorna objetos
       ↓
┌──────────────┐
│   service/   │  ← Recibe objetos del repository
└──────┬───────┘
       │ Retorna objetos
       ↓
┌──────────────┐
│     api/     │  ← Serializa con Pydantic schemas
└──────────────┘
```

## 📖 Para Aprender Más

1. Abre cada archivo (`user.py`, `trip.py`, etc.)
2. Observa las relaciones (`relationship`, `ForeignKey`)
3. Compara con los schemas en `app/schemas/`
4. Lee SQLAlchemy Relationships: https://docs.sqlalchemy.org/en/20/orm/relationships.html

**Siguiente paso:** Lee [`../../repository/Resumen.md`](../../repository/Resumen.md) para queries.
