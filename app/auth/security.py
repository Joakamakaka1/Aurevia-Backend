from passlib.context import CryptContext

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    return _pwd.hash(p)

def verify_password(plain: str, hashed: str) -> bool:
    return _pwd.verify(plain, hashed)
