# 📚 Resumen - Carpeta `app/db/`

## 📋 ¿Qué es este módulo?

La carpeta `app/db/` contiene toda la **configuración de base de datos** y los **modelos ORM** (Object-Relational Mapping). Es la capa que conecta Python con MySQL usando SQLAlchemy.

## 🎯 Responsabilidad

Este módulo es responsable de:

- ✅ Configurar conexión a MySQL
- ✅ Crear sesiones de base de datos
- ✅ Definir modelos ORM (tablas como clases Python)
- ✅ Crear tablas automáticamente
- ✅ Poblar base de datos con datos iniciales (seeding)

## 📁 Estructura de Archivos

```
db/
├── base.py         # Clase base para todos los modelos ORM
├── session.py      # Configuración de conexión y sesiones
├── seed.py         # Datos iniciales para desarrollo
└── models/         # Modelos ORM (entidades)
    ├── __init__.py
    ├── user.py     # Modelo User
    ├── trip.py     # Modelo Trip
    ├── country.py  # Modelo Country
    ├── city.py     # Modelo City
    └── comment.py  # Modelo Comment
```

## 🛠️ Tecnologías Usadas

| Tecnología                 | Propósito                                |
| -------------------------- | ---------------------------------------- |
| **SQLAlchemy 2.x**         | ORM (mapear objetos Python ↔ tablas SQL) |
| **mysql-connector-python** | Driver para conectar con MySQL           |
| **MySQL 8.0+**             | Base de datos relacional                 |

## 📄 Archivos Principales

### 1️⃣ `session.py` - Conexión a Base de Datos

**Propósito:** Configurar la conexión con MySQL y crear sesiones.

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Crear motor de base de datos
engine = create_engine(
    settings.database_url,  # mysql+mysqlconnector://user:pass@host:3306/db
    echo=settings.DEBUG,    # Log SQL queries si DEBUG=True
    pool_pre_ping=True      # Verificar conexión antes de usar
)

# Crear factory de sesiones
SessionLocal = sessionmaker(
    autocommit=False,  # Commit manual (o con @transactional)
    autoflush=False,   # Flush manual
    bind=engine        # Conectar al engine
)
```

**Concepto: SQLAlchemy Engine**

El **engine** es la conexión con la base de datos:

```
Python Code
    ↓
SQLAlchemy Engine  ← Gestiona pool de conexiones
    ↓
MySQL Driver (mysql-connector-python)
    ↓
MySQL Server
```

**Concepto: Session**

Una **Session** es una transacción con la BD:

```python
db = SessionLocal()  # Abrir sesión
try:
    user = db.query(User).first()  # Query
    db.commit()  # Guardar cambios
finally:
    db.close()  # Cerrar sesión
```

---

### 2️⃣ `base.py` - Clase Base

**Propósito:** Clase base para todos los modelos ORM.

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Clase base para todos los modelos"""
    pass
```

**Uso:**

```python
# Todos los modelos heredan de Base
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    ...
```

**¿Por qué DeclarativeBase?**

SQLAlchemy 2.x usa `DeclarativeBase` en vez de `declarative_base()`:

```python
# SQLAlchemy 1.x (antiguo)
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# SQLAlchemy 2.x (nuevo)
from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase):
    pass
```

---

### 3️⃣ `seed.py` - Datos Iniciales

**Propósito:** Poblar la base de datos con datos de prueba para desarrollo.

```python
from sqlalchemy.orm import Session
from app.db.models import User, Country, City, Trip, Comment
from app.auth.security import hash_password

def seed_db(db: Session):
    """Poblar base de datos con datos iniciales"""

    # Verificar si ya hay datos
    if db.query(User).first():
        print("✅ Base de datos ya tiene datos, saltando seeding")
        return

    print("🌱 Iniciando seeding de base de datos...")

    # 1. Crear usuarios
    users = [
        User(
            email="admin@aurevia.com",
            username="admin",
            hashed_password=hash_password("password123"),
            role="admin"
        ),
        User(
            email="john@example.com",
            username="johndoe",
            hashed_password=hash_password("password123"),
            role="user"
        ),
        # ... más usuarios
    ]
    db.add_all(users)
    db.commit()

    # 2. Crear países
    countries = [
        Country(name="Spain"),
        Country(name="France"),
        Country(name="Italy"),
        Country(name="Japan"),
        Country(name="USA"),
    ]
    db.add_all(countries)
    db.commit()

    # 3. Crear ciudades
    cities = [
        City(name="Madrid", country_id=1, latitude=40.4168, longitude=-3.7038),
        City(name="Barcelona", country_id=1, latitude=41.3851, longitude=2.1734),
        # ... más ciudades
    ]
    db.add_all(cities)
    db.commit()

    # 4. Crear viajes
    trips = [
        Trip(
            name="Aventura en Madrid",
            description="Un viaje increíble por la capital española",
            start_date=date(2024, 6, 1),
            end_date=date(2024, 6, 10),
            user_id=1,
            country_id=1
        ),
        # ... más viajes
    ]
    db.add_all(trips)
    db.commit()

    # 5. Crear comentarios
    comments = [
        Comment(
            content="¡Qué viaje tan increíble!",
            user_id=2,
            trip_id=1
        ),
        # ... más comentarios
    ]
    db.add_all(comments)
    db.commit()

    print("✅ Seeding completado!")
```

**Llamado desde main.py:**

```python
from app.db.seed import seed_db
from app.db.session import SessionLocal

try:
    db = SessionLocal()
    seed_db(db)  # Solo pobla si está vacía
finally:
    db.close()
```

**Contraseña de usuarios de prueba:** `password123`

---

### 4️⃣ `models/` - Modelos ORM

Ver [`models/Resumen.md`](models/Resumen.md) para detalles de cada modelo.

**Entidades implementadas:**

- **User** - Usuarios con autenticación
- **Trip** - Viajes de usuarios
- **Country** - Países visitables
- **City** - Ciudades en países
- **Comment** - Comentarios en viajes

## 🔄 Flujo de Creación de Tablas

Cuando inicias la aplicación:

```
1️⃣ main.py se ejecuta
   ↓
2️⃣ Importa db.base → Define Base
   ↓
3️⃣ Importa db.models → Define User, Trip, etc.
   ↓ Todos heredan de Base

4️⃣ Base.metadata.create_all(bind=engine)
   ↓ SQLAlchemy inspecciona modelos
   ↓ Genera SQL CREATE TABLE

5️⃣ MySQL crea tablas si no existen
   ↓
   CREATE TABLE users (
       id INT AUTO_INCREMENT PRIMARY KEY,
       email VARCHAR(255) UNIQUE NOT NULL,
       username VARCHAR(255) UNIQUE NOT NULL,
       hashed_password VARCHAR(255) NOT NULL,
       role ENUM('user', 'admin', 'superadmin') DEFAULT 'user'
   );

6️⃣ seed_db(db) pobla datos iniciales
   ↓ Solo si está vacía
```

## 💡 Conceptos Clave de SQLAlchemy

### 1. **ORM (Object-Relational Mapping)**

Mapea clases Python ↔ tablas SQL:

```python
# Clase Python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)

# ↕ SQLAlchemy traduce a SQL

# Tabla SQL
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL
);
```

**Operaciones:**

```python
# Python ORM
user = User(email="test@mail.com")
db.add(user)
db.commit()

# ↓ SQLAlchemy genera

# SQL
INSERT INTO users (email) VALUES ('test@mail.com');
```

### 2. **Session (Transacción)**

Una **Session** agrupa operaciones en una transacción:

```python
db = SessionLocal()

# Transacción
user1 = User(email="user1@mail.com")
user2 = User(email="user2@mail.com")
db.add(user1)
db.add(user2)

# Si falla aquí, ninguno se guarda (atomicidad)
db.commit()  # ✅ Ambos se guardan
# o
db.rollback()  # ❌ Ninguno se guarda
```

### 3. **Mapped Columns**

SQLAlchemy 2.x usa tipado moderno:

```python
# Nuevo (SQLAlchemy 2.x)
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255))
    age: Mapped[Optional[int]] = mapped_column(nullable=True)

# Antiguo (SQLAlchemy 1.x)
from sqlalchemy import Column, Integer, String

class User(Base):
    id = Column(Integer, primary_key=True)
    email = Column(String(255))
```

### 4. **Relationships**

Relaciones entre tablas:

```python
class User(Base):
    trips = relationship("Trip", back_populates="user")
    # User tiene muchos Trip

class Trip(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user = relationship("User", back_populates="trips")
    # Trip pertenece a un User
```

**Uso:**

```python
user = db.query(User).first()
print(user.trips)  # SQLAlchemy carga automáticamente
# SELECT * FROM trips WHERE user_id = ?
```

### 5. **Eager Loading (joinedload)**

Cargar relaciones en una sola query:

```python
# ❌ N+1 Problem (malo)
users = db.query(User).all()
for user in users:
    print(user.trips)  # 1 query por cada user

# ✅ Eager Loading (bueno)
from sqlalchemy.orm import joinedload
users = db.query(User).options(joinedload(User.trips)).all()
# SELECT * FROM users JOIN trips ON ... (1 sola query)
for user in users:
    print(user.trips)  # Ya cargados, sin query extra
```

## 🔗 Relación con Otros Módulos

```
┌──────────────┐
│  main.py     │  ← Crea tablas, hace seeding
└──────┬───────┘
       │
       ↓
┌──────────────┐
│     db/      │  ← ESTÁS AQUÍ
│  session.py  │    Proporciona engine, SessionLocal
│  models/     │    Define estructura de tablas
└──────┬───────┘
       │
       ↓
┌──────────────┐
│  repository/ │  ← Usa Session para queries
└──────────────┘
       │
       ↓
┌──────────────┐
│    MySQL     │  ← Almacena datos
└──────────────┘
```

## 📖 Para Aprender Más

1. Lee `models/Resumen.md` para ver las entidades
2. Revisa `session.py` para conexión
3. Estudia SQLAlchemy 2.0: https://docs.sqlalchemy.org/
4. Investiga patrón Unit of Work (Session)

**Siguiente paso:** Lee [`models/Resumen.md`](models/Resumen.md) para los modelos ORM.
