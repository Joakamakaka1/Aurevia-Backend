# 📚 Resumen - Carpeta `app/service/`

## 📋 ¿Qué es este módulo?

La carpeta `app/service/` contiene la **capa de lógica de negocio** (Business Logic Layer). Es donde viven las reglas y validaciones específicas de tu aplicación.

## 🎯 Responsabilidad

Este módulo es responsable de:

- ✅ **Implementar reglas de negocio** (validaciones complejas)
- ✅ **Coordinar operaciones** entre múltiples repositories
- ✅ **Validar consistencia** de datos
- ✅ **Manejar transacciones** con `@transactional`
- ✅ **Lanzar excepciones** de negocio (`AppError`)

**⚠️ Lo que NO hace:**

- ❌ No hace queries directos (usa `repository/`)
- ❌ No valida formato de entrada (usa `schemas/`)
- ❌ No maneja HTTP (usa `api/endpoints/`)

## 📁 Estructura de Archivos

```
service/
├── city.py          # Lógica de negocio de ciudades
├── comment.py       # Lógica de negocio de comentarios
├── country.py       # Lógica de negocio de países
├── friendship.py    # Lógica de negocio de amistad (comentado)
├── trip.py          # Lógica de negocio de viajes
└── user.py          # Lógica de negocio de usuarios
```

## 🛠️ Patrón Service Layer

### ¿Qué es el Service Layer?

Es una capa intermedia que contiene **lógica de negocio**:

```
┌──────────────┐
│  Endpoints   │  ← Recibe HTTP, delega a Service
└──────┬───────┘
       │
       ↓
┌──────────────┐
│   Service    │  ← LÓGICA DE NEGOCIO
└──────┬───────┘  ← Valida, coordina, decide
       │
       ↓
┌──────────────┐
│  Repository  │  ← Solo queries SQL
└──────────────┘
```

**Ejemplos de Lógica de Negocio:**

- ✅ Validar que el email no esté duplicado
- ✅ Verificar que end_date >= start_date
- ✅ Asegurar que el país existe antes de crear viaje
- ✅ Hashear password antes de guardar
- ✅ Coordinar creación de entidades relacionadas

## 📝 Ejemplo: UserService

```python
from sqlalchemy.orm import Session
from app.db.models.user import User
from app.auth.security import verify_password, hash_password
from app.core.exceptions import AppError
from app.core.constants import ErrorCode
from app.core.decorators import transactional
from app.repository.user import UserRepository

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Obtener todos los usuarios con paginación"""
        return self.repo.get_all(skip=skip, limit=limit)

    def get_by_email(self, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        return self.repo.get_by_email(email)

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Obtener usuario por ID"""
        return self.repo.get_by_id(user_id)

    @transactional
    def create(self, *, email: str, username: str, password: str, role: str = "user") -> User:
        """
        Crear nuevo usuario.

        Lógica de negocio:
        1. Validar que email no esté duplicado
        2. Validar que username no esté duplicado
        3. Hashear password
        4. Crear usuario en BD
        """
        # VALIDACIÓN 1: Email duplicado
        if self.repo.get_by_email(email):
            raise AppError(409, ErrorCode.EMAIL_DUPLICATED, "El email ya está registrado")

        # VALIDACIÓN 2: Username duplicado
        if self.repo.get_by_username(username):
            raise AppError(409, ErrorCode.USERNAME_DUPLICATED, "El username ya está registrado")

        # TRANSFORMACIÓN: Hashear password
        hashed_pwd = hash_password(password)

        # CREAR: Delegar a repository
        user = User(email=email, username=username, hashed_password=hashed_pwd, role=role)
        return self.repo.create(user)
        # @transactional hace commit automáticamente

    def authenticate(self, *, email: str, password: str) -> User:
        """
        Autenticar usuario.

        Lógica de negocio:
        1. Verificar que email exista
        2. Verificar que password coincida
        """
        # VALIDACIÓN 1: Email existe
        user = self.repo.get_by_email(email)
        if not user:
            raise AppError(404, ErrorCode.EMAIL_NOT_FOUND, "El email no existe")

        # VALIDACIÓN 2: Password correcta
        if not verify_password(password, user.hashed_password):
            raise AppError(400, ErrorCode.INVALID_PASSWORD, "La contraseña es incorrecta")

        return user

    def login(self, *, email: str, password: str) -> dict:
        """
        Autentica y genera tokens JWT.
        """
        # 1. Autenticar credenciales
        user = self.authenticate(email=email, password=password)

        # 2. Generar tokens
        token_data = {"user_id": user.id, "username": user.username, "role": user.role}
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user
        }

    def refresh_token(self, refresh_token: str) -> dict:
        """
        Renueva access token usando refresh token.
        """
        try:
            # 1. Validar refresh token
            token_data = decode_refresh_token(refresh_token)

            # 2. Verificar usuario en BD (importante por seguridad)
            user = self.repo.get_by_id(token_data.get("user_id"))
            if not user:
                raise AppError(401, "USER_NOT_FOUND", "Usuario no encontrado")

            # 3. Generar nuevos tokens
            new_data = {"user_id": user.id, "username": user.username, "role": user.role}
            return {
                "access_token": create_access_token(new_data),
                "refresh_token": create_refresh_token(new_data),
                "token_type": "bearer",
                "user": user
            }
        except Exception as e:
            raise AppError(401, "INVALID_TOKEN", str(e))

    @transactional
    def update(self, user_id: int, user_data: dict) -> User:
        """
        Actualizar usuario.

        Lógica de negocio:
        1. Verificar que usuario exista
        2. Validar email duplicado (si se está cambiando)
        3. Validar username duplicado (si se está cambiando)
        4. Hashear password (si se está cambiando)
        5. Actualizar en BD
        """
        user = self.repo.get_by_id(user_id)
        if not user:
            raise AppError(404, ErrorCode.USER_NOT_FOUND, "El usuario no existe")

        if 'email' in user_data and user_data['email'] is not None:
            existing = self.repo.get_by_email(user_data['email'])
            if existing and existing.id != user_id:
                raise AppError(409, ErrorCode.EMAIL_DUPLICATED, "Email ya usado")

        # ... (otras validaciones) ...

        if 'password' in user_data and user_data['password'] is not None:
            hashed = hash_password(user_data['password'])
            user_data['hashed_password'] = hashed
            del user_data['password']

        return self.repo.update(user_id, user_data)

    @transactional
    def delete(self, user_id: int) -> None:
        """Eliminar usuario."""
        user = self.repo.get_by_id(user_id)
        if not user:
            raise AppError(404, ErrorCode.USER_NOT_FOUND, "El usuario no existe")

        self.repo.delete(user)
```

## 💡 Conceptos Clave

### 1. **Decorador @transactional**

Maneja transacciones automáticamente:

```python
@transactional
def create_trip(self, ...):
    # Si algo falla aquí → ROLLBACK automático
    trip = Trip(...)
    self.trip_repo.create(trip)

    comment = Comment(trip_id=trip.id, ...)
    self.comment_repo.create(comment)

    # Si todo OK → COMMIT automático
    return trip
```

**Sin @transactional (tedioso):**

```python
def create_trip(self, ...):
    try:
        trip = Trip(...)
        self.trip_repo.create(trip)
        comment = Comment(...)
        self.comment_repo.create(comment)
        self.db.commit()  # Manual
        self.db.refresh(trip)  # Manual
        return trip
    except Exception:
        self.db.rollback()  # Manual
        raise
```

### 2. **Validaciones de Negocio**

No confundir con validaciones de formato (Pydantic):

```python
# ❌ Validación de FORMATO (va en schemas)
if not "@" in email:
    raise ValueError("Email inválido")

# ✅ Validación de NEGOCIO (va en service)
if self.repo.get_by_email(email):
    raise AppError(409, "Email ya registrado")
```

### 3. **Lanzar AppError**

Usa excepciones personalizadas para errores de negocio:

```python
# ✅ BUENO - AppError con código
if not user:
    raise AppError(404, ErrorCode.USER_NOT_FOUND, "Usuario no existe")

# ❌ MALO - Exception genérica
if not user:
    raise Exception("Usuario no existe")
```

### 4. **Dependency Injection**

Los services reciben la sesión de BD y crean sus repositories:

```python
class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)  # Crear repository
```

**Inyección en endpoints:**

```python
# api/deps.py
def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

# api/endpoints/user.py
@router.post("/")
def create_user(
    payload: UserCreate,
    service: UserService = Depends(get_user_service)  # ← Inyección
):
    return service.create(...)
```

## 🔄 Flujo Completo de una Operación

```
1️⃣ CLIENTE hace request
   POST /api/v1/trip/
   Body: {
     "name": "Viaje a París",
     "start_date": "2024-06-01",
     "end_date": "2024-05-20",  ← ¡Error de fecha!
     "country_id": 999  ← ¡País no existe!
   }

   ↓

2️⃣ ENDPOINT recibe y valida formato
   @router.post("/", response_model=TripOut)
   def create_trip(payload: TripCreate):  # ← Pydantic valida formato
       # ✅ Formato OK (fechas son dates válidos)
       return service.create(...)

   ↓

3️⃣ SERVICE valida negocio
   @transactional
   def create(self, ...):
       # VALIDACIÓN 1: Fechas coherentes
       if end_date < start_date:  # ← ❌ FALLA
           raise AppError(400, "end_date debe ser >= start_date")

       # (No llega aquí porque falla antes)
       # VALIDACIÓN 2: País existe
       if not self.country_repo.get_by_id(country_id):
           raise AppError(404, "País no existe")

       # CREAR: Delegar a repository
       trip = Trip(...)
       return self.trip_repo.create(trip)

   ↓

4️⃣ RESPUESTA de error
   400 Bad Request
   {
     "error": {
       "code": "INVALID_DATES",
       "message": "end_date debe ser >= start_date"
     }
   }
```

## 📊 Comparación: Service vs Repository

| Aspecto             | Service                 | Repository          |
| ------------------- | ----------------------- | ------------------- |
| **Responsabilidad** | Lógica de negocio       | Acceso a datos      |
| **Contiene**        | Validaciones, reglas    | Queries SQL         |
| **Usa**             | Repository              | Session (db.query)  |
| **Ejemplo**         | Validar email duplicado | get_by_email(email) |
| **Transacciones**   | @transactional          | NO hace commit      |

**Ejemplo:**

```python
# SERVICE - Lógica de negocio
class UserService:
    @transactional
    def create(self, email, username, password):
        # Validar email duplicado (REGLA DE NEGOCIO)
        if self.repo.get_by_email(email):
            raise AppError(409, "Email duplicado")

        # Hashear password (TRANSFORMACIÓN)
        hashed = hash_password(password)

        # Crear usuario (DELEGADO a repository)
        user = User(email=email, hashed_password=hashed)
        return self.repo.create(user)

# REPOSITORY - Acceso a datos
class UserRepository:
    def get_by_email(self, email):
        # Solo query SQL, sin lógica
        return self.db.query(User).filter(User.email == email).first()

    def create(self, user):
        # Solo INSERT, sin commit
        self.db.add(user)
        return user
```

## 🎯 Patrones Comunes

### 1. **Validación de Existencia**

```python
def update(self, trip_id, data):
    trip = self.repo.get_by_id(trip_id)
    if not trip:
        raise AppError(404, ErrorCode.TRIP_NOT_FOUND, "Viaje no existe")
    # ... actualizar
```

### 2. **Validación de Duplicados**

```python
def create(self, email, ...):
    if self.repo.get_by_email(email):
        raise AppError(409, ErrorCode.EMAIL_DUPLICATED, "Email ya existe")
    # ... crear
```

### 3. **Validación de Relaciones**

```python
def create_trip(self, country_id, ...):
    if not self.country_repo.get_by_id(country_id):
        raise AppError(404, ErrorCode.COUNTRY_NOT_FOUND, "País no existe")
    # ... crear viaje
```

### 4. **Coordinación de Múltiples Repos**

```python
@transactional
def create_trip_with_comment(self, trip_data, comment_text):
    # 1. Crear viaje
    trip = Trip(**trip_data)
    self.trip_repo.create(trip)

    # 2. Crear comentario inicial
    comment = Comment(trip_id=trip.id, content=comment_text)
    self.comment_repo.create(comment)

    # Ambos se guardan en la misma transacción
    return trip
```

## 🔗 Relación con Otros Módulos

```
┌──────────────┐
│     api/     │  ← Inyecta service, llama métodos
└──────┬───────┘
       │
       ↓
┌──────────────┐
│   service/   │  ← ESTÁS AQUÍ
└──────┬───────┘  ← Lógica de negocio
       │
       ↓
┌──────────────┐
│ repository/  │  ← Usa repositories para queries
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ db/models/   │  ← Crea/modifica objetos ORM
└──────────────┘
```

## 📖 Para Aprender Más

1. Abre `user.py` y observa las validaciones
2. Busca `@transactional` y ve qué métodos lo usan
3. Compara con `repository/user.py` para ver la diferencia
4. Lee sobre Service Layer Pattern

**Resumen completo:** Has revisado toda la arquitectura de la API. ¡Felicitaciones! 🎉
