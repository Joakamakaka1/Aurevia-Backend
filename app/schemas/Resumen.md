# 📚 Resumen - Carpeta `app/schemas/`

## 📋 ¿Qué es este módulo?

La carpeta `app/schemas/` contiene **modelos Pydantic** para validación de entrada y serialización de salida. Son como "contratos" que definen qué datos acepta y retorna la API.

## 🎯 Responsabilidad

Este módulo es responsable de:

- ✅ **Validar datos de entrada** (request body, query params)
- ✅ **Serializar respuestas** (objetos Python → JSON)
- ✅ **Definir tipos de datos** y formatos
- ✅ **Documentar la API** (schemas aparecen en Swagger)
- ✅ **Evitar referencias circulares** con schemas Basic/Out

**⚠️ Lo que NO hace:**

- ❌ No contiene lógica de negocio (va en `service/`)
- ❌ No define estructura de BD (va en `db/models/`)
- ❌ No hace queries (va en `repository/`)

## 📁 Estructura de Archivos

```
schemas/
├── city.py          # Schemas de ciudades
├── comment.py       # Schemas de comentarios
├── country.py       # Schemas de países
├── trip.py          # Schemas de viajes
└── user.py          # Schemas de usuarios y JWT
```

## 🛠️ Tecnologías Usadas

| Tecnología          | Propósito                      |
| ------------------- | ------------------------------ |
| **Pydantic 2.x**    | Validación de datos con tipado |
| **EmailStr**        | Validación de emails           |
| **field_validator** | Validadores personalizados     |
| **ConfigDict**      | Configuración del schema       |

## 💡 Schemas en Dos Niveles

Para evitar **referencias circulares**, usamos dos tipos de schemas:

### 1️⃣ **Basic** - Sin relaciones

Se usan **dentro de otros schemas** para evitar ciclos infinitos:

```python
# user.py
class UserBasic(BaseModel):
    """Schema básico de usuario para usar en relaciones"""
    id: int
    email: EmailStr
    username: str

    model_config = ConfigDict(from_attributes=True)

# trip.py usa UserBasic (no UserOut)
class TripOut(BaseModel):
    id: int
    name: str
    user: UserBasic  # ← Solo info básica del usuario
```

### 2️⃣ **Out** - Con relaciones completas

Se usan en **respuestas finales** de endpoints:

```python
# user.py
class UserOut(BaseModel):
    """Schema completo de usuario con relaciones"""
    id: int
    email: EmailStr
    username: str
    role: str
    trips: list[TripBasic] = []      # ← Relaciones anidadas
    comments: list[CommentBasic] = []

    model_config = ConfigDict(from_attributes=True)
```

### ❌ Problema: Referencias Circulares

Sin schemas Basic, tendríamos ciclos infinitos:

```python
# ❌ MALO - Referencia circular
class UserOut(BaseModel):
    trips: list[TripOut]  # Trip contiene User, User contiene Trip...

class TripOut(BaseModel):
    user: UserOut  # ← ¡Ciclo infinito!
```

### ✅ Solución: Schemas Basic

```python
# ✅ BUENO - Sin ciclos
class UserBasic(BaseModel):
    id: int
    username: str
    # Sin relaciones

class TripBasic(BaseModel):
    id: int
    name: str
    # Sin relaciones

class UserOut(BaseModel):
    id: int
    username: str
    trips: list[TripBasic]  # ← Solo info básica

class TripOut(BaseModel):
    id: int
    name: str
    user: UserBasic  # ← Solo info básica
```

## 📝 Tipos de Schemas

### 1️⃣ **Create** - Para crear entidades

```python
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str  # En texto plano (se hashea en service)
    role: Optional[Literal["user", "admin", "superadmin"]] = "user"

    @field_validator('username')
    def validate_username_length(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError('Username debe tener al menos 3 caracteres')
        if len(v) > 50:
            raise ValueError('Username no puede tener más de 50 caracteres')
        return v

    @field_validator('password')
    def validate_password_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password debe tener al menos 8 caracteres')
        if len(v) > 72:  # Límite de Bcrypt
            raise ValueError('Password no puede tener más de 72 caracteres')
        return v
```

**Uso:**

```python
@router.post("/register", response_model=UserOut)
def register(payload: UserCreate):  # ← Pydantic valida automáticamente
    # Si payload es inválido, FastAPI retorna 422 automáticamente
    return service.create(...)
```

### 2️⃣ **Update** - Para actualizar entidades

```python
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[Literal["user", "admin", "superadmin"]] = None

    # Campos opcionales (solo se actualizan los proporcionados)
```

**Uso:**

```python
@router.put("/{user_id}")
def update_user(user_id: int, payload: UserUpdate):
    # Excluir campos no proporcionados
    data = payload.model_dump(exclude_unset=True)
    # data = {"email": "new@mail.com"} (solo email si es lo único enviado)
    return service.update(user_id, data)
```

### 3️⃣ **Out** - Para respuestas

```python
class UserOut(BaseModel):
    """Schema completo para respuestas"""
    id: int
    email: EmailStr
    username: str
    role: str
    trips: list[TripBasic] = []
    comments: list[CommentBasic] = []

    model_config = ConfigDict(from_attributes=True)
```

**ConfigDict `from_attributes=True`:**
Permite convertir objetos SQLAlchemy → Pydantic:

```python
# Objeto SQLAlchemy
user = User(id=1, email="test@mail.com", username="john")

# Pydantic lo serializa automáticamente
user_out = UserOut.model_validate(user)
# → {"id": 1, "email": "test@mail.com", "username": "john", ...}
```

### 4️⃣ **Otros** - Login, Token, etc.

```python
class UserLogin(BaseModel):
    """Para autenticación"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Respuesta de login"""
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class TokenData(BaseModel):
    """Datos dentro del JWT"""
    user_id: int
    username: str
    role: str
```

## 🔄 Flujo de Validación

```
1️⃣ CLIENTE envía request
   POST /api/v1/auth/register
   Body: {"email": "test@mail.com", "username": "jo", "password": "123"}

   ↓

2️⃣ FASTAPI recibe y valida con Pydantic
   payload: UserCreate

   ↓ Validaciones:

   ✅ email es EmailStr → OK
   ❌ username tiene 2 chars → ERROR (mínimo 3)
   ❌ password tiene 3 chars → ERROR (mínimo 8)

   ↓

3️⃣ RESPUESTA de error automática
   422 Unprocessable Entity
   {
     "error": {
       "code": "VALIDATION_ERROR",
       "message": "Error de validación"
     },
     "details": [
       {
         "field": "username",
         "message": "Username debe tener al menos 3 caracteres"
       },
       {
         "field": "password",
         "message": "Password debe tener al menos 8 caracteres"
       }
     ]
   }
```

## 💡 Validadores Personalizados

### Validador de Campo

```python
@field_validator('email')
@classmethod
def validate_email_format(cls, v: str) -> str:
    """Valida formato de email"""
    # Lógica personalizada
    if not "@" in v:
        raise ValueError("Email inválido")
    return v
```

### Validador de Modelo

```python
@model_validator(mode='after')
def validate_dates(self) -> 'TripCreate':
    """Valida que end_date >= start_date"""
    if self.end_date < self.start_date:
        raise ValueError('La fecha de fin debe ser posterior a la de inicio')
    return self
```

## 📊 Diferencia: Pydantic vs SQLAlchemy

| Aspecto        | SQLAlchemy (Models) | Pydantic (Schemas)     |
| -------------- | ------------------- | ---------------------- |
| **Propósito**  | Estructura de BD    | Validación de datos    |
| **Ubicación**  | `db/models/`        | `schemas/`             |
| **Uso**        | ORM (queries SQL)   | API (request/response) |
| **Relaciones** | `relationship()`    | Lista de schemas Basic |
| **Validación** | Constraints SQL     | Validators Python      |

**Ejemplo:**

```python
# SQLAlchemy Model (db/models/user.py)
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    trips = relationship("Trip", back_populates="user")
    # Para BD

# Pydantic Schema (schemas/user.py)
class UserOut(BaseModel):
    id: int
    email: EmailStr
    trips: list[TripBasic] = []
    # Para API
```

## 🔗 Relación con Otros Módulos

```
┌──────────────┐
│     api/     │  ← Usa schemas para validar request/response
└──────┬───────┘
       │
       ↓
┌──────────────┐
│   schemas/   │  ← ESTÁS AQUÍ
└──────────────┘  ← Valida y serializa
       ↓
┌──────────────┐
│   service/   │  ← Recibe datos ya validados
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ db/models/   │  ← Pydantic serializa estos objetos
└──────────────┘
```

## 📖 Ejemplo Completo: Trip

```python
# schemas/trip.py

# 1. Schema Basic (sin relaciones)
class TripBasic(BaseModel):
    id: int
    name: str
    start_date: date
    end_date: date
    model_config = ConfigDict(from_attributes=True)

# 2. Schema Create (entrada)
class TripCreate(BaseModel):
    name: str
    description: str
    start_date: date
    end_date: date
    user_id: int
    country_id: int

    @field_validator('name')
    def validate_name(cls, v):
        if len(v) < 3 or len(v) > 100:
            raise ValueError("Nombre debe tener entre 3 y 100 caracteres")
        return v

    @model_validator(mode='after')
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("Fecha fin debe ser >= fecha inicio")
        return self

# 3. Schema Update (actualización)
class TripUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    country_id: Optional[int] = None

# 4. Schema Out (respuesta)
class TripOut(BaseModel):
    id: int
    name: str
    description: str
    start_date: date
    end_date: date
    user: UserBasic              # ← Info básica del usuario
    country: CountryBasic        # ← Info básica del país
    comments: list[CommentBasic] = []  # ← Comentarios

    model_config = ConfigDict(from_attributes=True)
```

**Uso en endpoint:**

```python
@router.post("/", response_model=TripOut)
def create_trip(payload: TripCreate):  # ← Valida entrada
    trip = service.create(...)
    return trip  # ← Pydantic serializa con TripOut
```

## 📝 Tips y Buenas Prácticas

1. **Siempre usa schemas Basic para relaciones** → Evita ciclos
2. **Usa `exclude_unset=True` en Update** → Solo actualiza campos enviados
3. **field_validator para validaciones simples** → Longitud, formato
4. **model_validator para validaciones complejas** → Relaciones entre campos
5. **ConfigDict(from_attributes=True)** → Para serializar modelos SQLAlchemy

**Siguiente paso:** Lee [`../service/Resumen.md`](../service/Resumen.md) para lógica de negocio.
