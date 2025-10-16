from passlib.context import CryptContext

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    return _pwd.hash(p[:72])

def verify_password(plain: str, hashed: str) -> bool:
    # Si el valor almacenado parece ser un hash bcrypt, verificar con passlib.
    if isinstance(hashed, str) and hashed.startswith("$2"):
        return _pwd.verify(plain[:72], hashed)
    # Si no, comparar en claro (inseguro, solo temporal)
    return plain == hashed