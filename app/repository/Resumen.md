# 📚 Resumen - Carpeta `app/repository/`

## 📋 ¿Qué es este módulo?

La carpeta `app/repository/` implementa el **patrón Repository**, que encapsula toda la lógica de acceso a datos (queries SQL) en clases especializadas.

## 🎯 Responsabilidad

Este módulo es responsable de:

- ✅ Ejecutar queries SQL usando SQLAlchemy
- ✅ Realizar operaciones CRUD (Create, Read, Update, Delete)
- ✅ Optimizar queries con eager loading (`joinedload`)
- ✅ Encapsular lógica de acceso a datos

**⚠️ Lo que NO hace:**

- ❌ No contiene lógica de negocio (eso va en `service/`)
- ❌ No hace commit/rollback (lo hace `@transactional` en service)
- ❌ No valida datos de negocio (lo hace service)

## 📁 Estructura de Archivos

```
repository/
├── city.py       # Queries de ciudades
├── comment.py    # Queries de comentarios
├── country.py    # Queries de países
├── trip.py       # Queries de viajes
└── user.py       # Queries de usuarios
```

## 🛠️ Patrón Repository

### ¿Qué es el Patrón Repository?

El **Repository Pattern** separa la lógica de acceso a datos de la lógica de negocio:

```
❌ MALO - Service hace queries directos
┌──────────────┐
│   Service    │  db.query(User).filter(...).first()
│  (Negocio)   │  db.query(Trip).join(...).all()
└──────┬───────┘  (SQL mezclado con lógica de negocio)
       │
       ↓
    MySQL

✅ BUENO - Repository encapsula queries
┌──────────────┐
│   Service    │  user_repo.get_by_email(email)
│  (Negocio)   │  trip_repo.get_all()
└──────┬───────┘  (Sin SQL, solo métodos claros)
       │
       ↓
┌──────────────┐
│  Repository  │  db.query(User).filter(User.email == email).first()
│   (Datos)    │  db.query(Trip).options(joinedload(...)).all()
└──────┬───────┘  (TODO el SQL aquí)
       │
       ↓
    MySQL
```

**Ventajas:**

- ✅ **Separación de responsabilidades** (SoC)
- ✅ **Testeable** (fácil hacer mocks de repositories)
- ✅ **Reutilizable** (misma query en múltiples services)
- ✅ **Mantenible** (cambios SQL en un solo lugar)

## 📝 Ejemplo: UserRepository

```python
from sqlalchemy.orm import Session, joinedload
from app.db.models.user import User
from typing import List, Optional

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Obtener todos los usuarios con sus relaciones"""
        return (
            self.db.query(User)
            .options(
                joinedload(User.trips),      # Eager load trips
                joinedload(User.comments)    # Eager load comments
            )
            .offset(skip).limit(limit)
            .all()
        )

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Obtener usuario por ID (con relaciones)"""
        return (
            self.db.query(User)
            .options(joinedload(User.trips), joinedload(User.comments))
            .filter(User.id == user_id)
            .first()
        )

    def get_by_id_light(self, user_id: int) -> Optional[User]:
        """
        Versión ligera sin relaciones.
        Útil para validaciones rápidas (ej. en refresh_token).
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        return (
            self.db.query(User)
            .options(joinedload(User.trips), joinedload(User.comments))
            .filter(User.email == email)
            .first()
        )

    # ... get_by_username ...

    def create(self, user: User) -> User:
        """Crear nuevo usuario (sin commit)"""
        self.db.add(user)
        self.db.flush()  # Generar ID
        return user

    def update(self, user_id: int, user_data: dict) -> User:
        """Actualizar usuario"""
        user = self.get_by_id(user_id)
        if not user:
            raise AppError(404, ErrorCode.USER_NOT_FOUND, "Usuario no existe")

        # Actualizar campos dinámicamente
        for key, value in user_data.items():
            if value is not None:
                setattr(user, key, value)

        return user  # @transactional en service hará el commit

    def delete(self, user: User) -> None:
        """Eliminar usuario"""
        self.db.delete(user)
```

## 💡 Conceptos Clave

### 1. **Eager Loading con joinedload**

#### Problema: N+1 Queries

```python
# ❌ MALO - N+1 problem
users = db.query(User).all()  # 1 query
for user in users:            # Loop
    print(user.trips)          # N queries (1 por cada user)

# Total: 1 + N queries
```

#### Solución: joinedload

```python
# ✅ BUENO - 1 query total
users = (
    db.query(User)
    .options(joinedload(User.trips))  # JOIN en SQL
    .all()
)
for user in users:
    print(user.trips)  # Ya cargados, 0 queries extra

# Total: 1 query
```

**SQL generado:**

```sql
SELECT users.*, trips.*
FROM users
LEFT JOIN trips ON trips.user_id = users.id
```

### 2. **Operaciones CRUD Estándar**

Todos los repositories tienen estos métodos básicos:

```python
class SomeRepository:
    def get_all(skip=0, limit=100) -> List[Model]:        # SELECT * LIMIT ? OFFSET ?
    def get_by_id(id) -> Optional[Model]: # SELECT WHERE id = ?
    def create(model) -> Model:          # INSERT
    def update(id, data) -> Model:       # UPDATE
    def delete(model) -> None:           # DELETE
```

### 3. **Session pero NO Commit**

Los repositories usan `self.db` pero **NO hacen commit**:

```python
def create(self, user: User) -> User:
    self.db.add(user)
    # ❌ NO: self.db.commit()
    return user  # El commit lo hace @transactional en service
```

**¿Por qué?**

- El service puede hacer múltiples operaciones antes de commit
- `@transactional` hace commit/rollback de forma consistente

### 4. **Queries Específicas**

Además de CRUD básico, puedes agregar queries específicas:

```python
class TripRepository:
    # ... CRUD básico ...

    def get_by_country(self, country_id: int) -> List[Trip]:
        """Todos los viajes a un país"""
        return (
            self.db.query(Trip)
            .filter(Trip.country_id == country_id)
            .all()
        )

    def get_by_user(self, user_id: int) -> List[Trip]:
        """Todos los viajes de un usuario"""
        return (
            self.db.query(Trip)
            .filter(Trip.user_id == user_id)
            .all()
        )

    def get_recent(self, limit: int = 10) -> List[Trip]:
        """Viajes más recientes"""
        return (
            self.db.query(Trip)
            .order_by(Trip.start_date.desc())
            .limit(limit)
            .all()
        )
```

## 🔄 Flujo de Uso

```
1️⃣ ENDPOINT recibe petición
   POST /api/v1/auth/register
   Body: {"email": "new@mail.com", "username": "john", "password": "123"}

   ↓

2️⃣ Inyectar UserService
   service: UserService = Depends(get_user_service)

   ↓

3️⃣ SERVICE Layer (lógica de negocio)
   @transactional
   def create(self, email, username, password):
       # Validar email duplicado
       if self.repo.get_by_email(email):  # ← Llama repository
           raise AppError(409, "Email duplicado")

       # Crear usuario
       user = User(email=email, ...)
       return self.repo.create(user)  # ← Llama repository

   ↓

4️⃣ REPOSITORY Layer (acceso a datos)
   def get_by_email(self, email):
       return db.query(User).filter(User.email == email).first()

   def create(self, user):
       db.add(user)
       return user  # Sin commit

   ↓

5️⃣ @transactional hace commit
   db.commit()
   db.refresh(user)

   ↓

6️⃣ Respuesta al cliente
   201 Created
   {"id": 1, "email": "new@mail.com", ...}
```

## 📊 Comparación: Con vs Sin Repository

### Sin Repository (malo)

```python
# Service con SQL directo
class UserService:
    def get_by_email(self, email):
        # SQL mezclado con lógica de negocio
        return self.db.query(User).filter(User.email == email).first()

    def create(self, email, username, password):
        # Duplicado en múltiples services
        user = self.db.query(User).filter(User.email == email).first()
        if user:
            raise AppError(...)

        new_user = User(email=email, ...)
        self.db.add(new_user)
        self.db.commit()
        return new_user
```

### Con Repository (bueno)

```python
# Repository encapsula SQL
class UserRepository:
    def get_by_email(self, email):
        return self.db.query(User).filter(User.email == email).first()

    def create(self, user):
        self.db.add(user)
        return user

# Service limpio, sin SQL
class UserService:
    @transactional
    def create(self, email, username, password):
        if self.repo.get_by_email(email):  # Reutiliza método
            raise AppError(...)

        user = User(email=email, ...)
        return self.repo.create(user)  # Reutiliza método
```

## 🔗 Relación con Otros Módulos

```
┌──────────────┐
│   api/       │  ← Inyecta service
└──────┬───────┘
       │
       ↓
┌──────────────┐
│  service/    │  ← Llama a repository
└──────┬───────┘  ← @transactional hace commit
       │
       ↓
┌──────────────┐
│ repository/  │  ← ESTÁS AQUÍ
└──────┬───────┘  ← Construye queries SQL
       │
       ↓
┌──────────────┐
│ db/models/   │  ← Define estructura de tablas
└──────┬───────┘
       │
       ↓
    MySQL
```

## 📖 Para Aprender Más

1. Abre `user.py` y observa los métodos
2. Compara con `service/user.py` para ver cómo se usa
3. Lee sobre Repository Pattern
4. Investiga query optimization en SQLAlchemy

**Siguiente paso:** Lee [`../schemas/Resumen.md`](../schemas/Resumen.md) para validación.
