from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from app.core.config import settings

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT con los datos proporcionados.
    
    Args:
        data: Diccionario con los datos a incluir en el token (user_id, role, etc.)
        expires_delta: Tiempo de expiración opcional. Si no se provee, usa el valor por defecto de config
    
    Returns:
        str: Token JWT codificado
    """
    to_encode = data.copy()
    
    # Establecer tiempo de expiración
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Agregar claim de expiración
    to_encode.update({"exp": expire})
    
    # Crear el token
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica un token JWT y retorna los datos.
    
    Args:
        token: Token JWT a decodificar
        
    Returns:
        Optional[dict]: Datos del token si es válido, None si es inválido o expirado
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        # Token expirado
        return None
    except jwt.JWTError:
        # Token inválido
        return None
