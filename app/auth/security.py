from passlib.context import CryptContext

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    return _pwd.hash(p[:72])

def verify_password(plain: str, hashed: str) -> bool:
    return plain, hashed