# 📚 Resumen - Carpeta `app/auth/`

## 📋 ¿Qué es este módulo?

La carpeta `app/auth/` contiene el **sistema de autenticación y seguridad** de la API. Implementa:

- 🔐 **Autenticación JWT** (JSON Web Tokens)
- 🔒 **Hasheo de contraseñas** con Bcrypt
- 🛡️ **Dependencias de seguridad** para proteger endpoints

## 🎯 Responsabilidad

Este módulo se encarga de:

- ✅ Crear y validar tokens JWT
- ✅ Hashear contraseñas de manera segura
- ✅ Verificar contraseñas al hacer login
- ✅ Proporcionar dependencias para obtener sesión de BD
- ✅ (Futuro) Proteger endpoints con autenticación

## 📁 Estructura de Archivos

```
auth/
├── deps.py        # Dependencias: get_db, get_current_user (futuro)
├── jwt.py         # Crear y decodificar tokens JWT
└── security.py    # Hashear y verificar contraseñas
```

## 🛠️ Tecnologías Usadas

| Tecnología  | Versión | Propósito                                |
| ----------- | ------- | ---------------------------------------- |
| **PyJWT**   | 2.10.1  | Crear y decodificar tokens JWT           |
| **Passlib** | 1.7.4   | Framework de hashing de passwords        |
| **Bcrypt**  | 3.2.2   | Algoritmo de hashing (usado por Passlib) |

## 📄 Archivos Principales

### 1️⃣ `security.py` - Seguridad de Contraseñas

**Propósito:** Hashear y verificar contraseñas de manera segura usando Bcrypt.

#### 🔑 ¿Qué es Bcrypt?

**Bcrypt** es un algoritmo de hashing diseñado para contraseñas:

- ✅ **Lento** (intencional) → dificulta ataques de fuerza bruta
- ✅ **Salt automático** → cada hash es único aunque la password sea igual
- ✅ **Adaptativo** → se puede ajustar la dificultad con el tiempo

#### 📝 Funciones Principales

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hashea una contraseña en texto plano.

    Args:
        password: "miPassword123"

    Returns:
        "$2b$12$KIXn3wxPa.vL8QZE6..." (hash bcrypt)
    """
    truncated = password[:72]  # Bcrypt tiene límite de 72 bytes
    return pwd_context.hash(truncated)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.

    Args:
        plain_password: "miPassword123"
        hashed_password: "$2b$12$KIXn3wxPa.vL8QZE6..."

    Returns:
        True si coincide, False si no
    """
    truncated = plain_password[:72]
    return pwd_context.verify(truncated, hashed_password)
```

#### 🔄 Flujo de Registro

```
1. Usuario se registra
   ↓ Password: "miPassword123"

2. hash_password("miPassword123")
   ↓ Bcrypt genera salt aleatorio
   ↓ Hash = "$2b$12$KIXn3wxPa.vL8QZE6nxL9u..."

3. Guardar en BD
   ↓ users.hashed_password = "$2b$12$..."
```

#### 🔄 Flujo de Login

```
1. Usuario hace login
   ↓ Envía: "miPassword123"

2. Obtener hash de BD
   ↓ hashed = "$2b$12$KIXn3wxPa.vL8QZE6..."

3. verify_password("miPassword123", hashed)
   ↓ Bcrypt rehashea con el mismo salt
   ↓ Compara hashes
   ↓ Return: True ✅
```

---

### 2️⃣ `jwt.py` - Tokens JWT

**Propósito:** Crear y decodificar tokens JWT para autenticación stateless.

#### 🔑 ¿Qué es JWT?

**JWT (JSON Web Token)** es un estándar para crear tokens de autenticación:

- ✅ **Stateless** → El servidor no necesita guardar sesiones
- ✅ **Self-contained** → El token contiene toda la info del usuario
- ✅ **Firmado** → No se puede alterar sin la SECRET_KEY

#### 📐 Estructura de un JWT

Un JWT tiene 3 partes separadas por puntos:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImpvaG4iLCJyb2xlIjoidXNlciIsImV4cCI6MTczMzQyNTIwMH0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
│                                      │                                                                                        │
Header (algoritmo)                      Payload (datos)                                                               Signature (firma)
```

**Decodificado:**

```json
// Header
{
  "alg": "HS256",
  "typ": "JWT"
}

// Payload (los datos que guardamos)
{
  "user_id": 1,
  "username": "john",
  "role": "user",
  "exp": 1733425200  // Timestamp de expiración
}

// Signature (firma con SECRET_KEY)
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  SECRET_KEY
)
```

#### 📝 Funciones Principales

```python
import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT con información del usuario.

    Args:
        data: {"user_id": 1, "username": "john", "role": "user"}
        expires_delta: Tiempo de expiración (opcional)

    Returns:
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    """
    to_encode = data.copy()

    # Calcular expiración (default: 1440 min = 24h)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Agregar claim de expiración
    to_encode.update({"exp": expire})

    # Firmar con SECRET_KEY
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica y valida un token JWT.

    Args:
        token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

    Returns:
        {"user_id": 1, "username": "john", "role": "user", "exp": ...}
        None si el token es inválido o expirado
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expirado
    except jwt.JWTError:
        return None  # Token inválido
```

#### 🔄 Flujo de Autenticación JWT

```
1️⃣ LOGIN
   POST /api/v1/auth/login
   Body: {"email": "user@mail.com", "password": "123"}

   ↓ Verificar password con verify_password()
   ↓ Si OK, crear token:

   token = create_access_token({
       "user_id": 1,
       "username": "john",
       "role": "user"
   })

   Response: {"access_token": "eyJ...", "user": {...}}

2️⃣ USAR TOKEN en peticiones posteriores
   GET /api/v1/trip/
   Headers: Authorization: Bearer eyJ...

   ↓ (Futuro) Middleware extrae token
   ↓ decode_access_token("eyJ...")
   ↓ Si válido → permite acceso
   ↓ Si inválido → 401 Unauthorized

3️⃣ TOKEN EXPIRA después de 24h (configurable)
   ↓ Usuario debe hacer login de nuevo
```

---

### 3️⃣ `deps.py` - Dependencias

**Propósito:** Proveer dependencias compartidas para inyectar en endpoints.

```python
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """
    Proporciona una sesión de base de datos.
    Se cierra automáticamente después de cada request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Uso en endpoints:**

```python
@router.get("/trips")
def get_trips(db: Session = Depends(get_db)):
    return db.query(Trip).all()
```

**Futuro: Proteger endpoints**

```python
# (No implementado aún)
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Obtiene el usuario actual desde el token JWT"""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(401, "Token inválido")

    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado")

    return user

# Usar en endpoints protegidos
@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

## 💡 Conceptos Clave

### 1. **Hashing vs Encryption**

| Concepto             | Reversible | Uso                                           |
| -------------------- | ---------- | --------------------------------------------- |
| **Hashing** (Bcrypt) | ❌ NO      | Passwords (nunca necesitas el texto original) |
| **Encryption** (AES) | ✅ SÍ      | Datos sensibles que necesitas leer después    |

```python
# Hashing (Bcrypt)
password = "secret123"
hashed = hash_password(password)  # "$2b$12$..."
# NO puedes obtener "secret123" desde "$2b$12$..."
# Solo puedes VERIFICAR si coinciden

# Encryption (ejemplo conceptual)
data = "tarjeta 1234-5678"
encrypted = encrypt(data, key)  # "Xk9pL..."
decrypted = decrypt(encrypted, key)  # "tarjeta 1234-5678"
```

### 2. **Salt**

Un **salt** es un valor aleatorio que se agrega antes de hashear:

```python
# Sin salt (MALO)
hash("password123") → siempre mismo hash
hash("password123") → atacante puede usar rainbow tables

# Con salt (BUENO - Bcrypt lo hace automático)
hash("password123" + salt1) → "$2b$12$abc..."
hash("password123" + salt2) → "$2b$12$xyz..."
# Mismo password, diferentes hashes → más seguro
```

### 3. **Stateless Authentication**

JWT permite autenticación **sin guardar sesiones** en el servidor:

**Tradicional (Stateful):**

```
Login → Server guarda sesión en BD
Cada request → Server busca sesión en BD
```

**JWT (Stateless):**

```
Login → Server crea JWT firmado
Cada request → Server solo verifica firma (sin BD)
```

**Ventajas:**

- ✅ Escala mejor (no BD por cada request)
- ✅ Funciona bien en microservicios
- ✅ Cliente puede llamar desde cualquier servidor

## 🔒 Seguridad

### Variables de Entorno Críticas

En `.env`:

```env
SECRET_KEY=tu-clave-super-secreta-minimo-32-caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 horas
```

### Límite de Bcrypt (72 bytes)

Bcrypt solo procesa los primeros 72 bytes:

```python
password = "a" * 100
hash_password(password)  # Solo hashea primeros 72 chars
```

Por eso el código trunca:

```python
truncated_password = password[:72]
```

## 🔗 Relación con Otros Módulos

```
┌──────────────┐
│  endpoints/  │  ← Llama a create_access_token() al hacer login
│   user.py    │    Llama a hash_password() al registrar
└──────┬───────┘
       │
       ↓
┌──────────────┐
│    auth/     │  ← ESTÁS AQUÍ
│  jwt.py      │    Crea/verifica tokens
│  security.py │    Hashea/verifica passwords
└──────┬───────┘
       │
       ↓
┌──────────────┐
│    core/     │  ← Lee SECRET_KEY, ALGORITHM de config
│  config.py   │
└──────────────┘
```

## 📖 Para Aprender Más

1. Lee `jwt.py` para entender tokens
2. Lee `security.py` para entender hashing
3. Prueba en https://jwt.io decodificar un token de tu API
4. Investiga Bcrypt: https://en.wikipedia.org/wiki/Bcrypt

**Siguiente paso:** Lee [`../core/Resumen.md`](../core/Resumen.md) para configuración.
